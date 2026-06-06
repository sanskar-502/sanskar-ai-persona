from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import os
from typing import List

load_dotenv()

from rag_engine import query_knowledge_base
from calendar_service import check_availability, book_interview
from prompts import SYSTEM_PROMPT
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sanskar AI Persona API")

# Add CORS middleware for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to the Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client once at startup
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Define tools for Gemini function calling ──
chat_tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="query_knowledge_base",
                description="Search Sanskar's knowledge base (resume, projects, skills) to answer specific questions about his background. Use this for any question about experience, projects, or technical skills.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(
                            type="STRING",
                            description="The search query to find relevant information",
                        )
                    },
                    required=["query"],
                ),
            ),
            types.FunctionDeclaration(
                name="check_availability",
                description="Check Sanskar's calendar for available interview slots. Call this when someone wants to schedule a meeting or interview.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "date_from": types.Schema(
                            type="STRING",
                            description="Start date in YYYY-MM-DD format (optional)",
                        ),
                        "date_to": types.Schema(
                            type="STRING",
                            description="End date in YYYY-MM-DD format (optional)",
                        ),
                    },
                ),
            ),
            types.FunctionDeclaration(
                name="book_interview",
                description="Book an interview slot on Sanskar's calendar. Requires the caller's name and email.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "start_time": types.Schema(
                            type="STRING",
                            description="The desired start time in ISO 8601 format",
                        ),
                        "name": types.Schema(
                            type="STRING",
                            description="The interviewer's name",
                        ),
                        "email": types.Schema(
                            type="STRING",
                            description="The interviewer's email",
                        ),
                    },
                    required=["start_time", "name", "email"],
                ),
            ),
        ]
    )
]

# Map function names to actual Python functions
TOOL_FUNCTIONS = {
    "query_knowledge_base": lambda args: query_knowledge_base(args.get("query", "")),
    "check_availability": lambda args: check_availability(args.get("date_from"), args.get("date_to")),
    "book_interview": lambda args: book_interview(args.get("start_time", ""), args.get("name", ""), args.get("email", "")),
}


# Models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

import time

def _call_gemini_with_retry(contents):
    """Wraps the Gemini API call with exponential backoff retries."""
    for attempt in range(5):
        try:
            return gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=1024,
                    tools=chat_tools,
                ),
            )
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < 4:
                    wait_time = (attempt + 1) * 3
                    logger.warning(f"Gemini API rate limit or unavailable. Retrying in {wait_time}s... (Attempt {attempt+1}/5)")
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint with Gemini function calling.
    The model can autonomously decide to query the knowledge base,
    check the calendar, or book an interview.
    """
    try:
        # Build conversation history for Gemini
        contents = []
        for msg in request.messages:
            role = "user" if msg.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))

        # Initial call with tools enabled
        response = _call_gemini_with_retry(contents)

        # ── Function-calling loop (max 5 rounds) ──
        for _ in range(5):
            # Check if the model wants to call a function
            candidate = response.candidates[0]
            function_calls = [
                part.function_call
                for part in candidate.content.parts
                if part.function_call
            ]

            if not function_calls:
                # No tool calls — model gave a final text answer
                break

            # Execute each function call and collect results
            function_responses = []
            for fc in function_calls:
                func_name = fc.name
                func_args = dict(fc.args) if fc.args else {}
                logger.info(f"Chat tool call: {func_name}({func_args})")

                executor = TOOL_FUNCTIONS.get(func_name)
                if executor:
                    result = executor(func_args)
                else:
                    result = f"Unknown function: {func_name}"

                function_responses.append(
                    types.Part.from_function_response(
                        name=func_name,
                        response={"result": result},
                    )
                )

            # Append the model's tool-call message + our results, then re-call
            contents.append(candidate.content)
            contents.append(types.Content(role="user", parts=function_responses))

            response = _call_gemini_with_retry(contents)

        # Extract final text
        final_text = response.text if response.text else "I couldn't generate a response. Please try again."
        return {"response": final_text}

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        # Return a friendly message instead of a 500 crash
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            return {"response": "I'm experiencing high demand right now. Please wait a few seconds and try again!"}
        elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return {"response": "I've hit my rate limit temporarily. Please wait about 15 seconds and try again!"}
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """
    Webhook for Vapi.ai server URL.
    Handles custom tool calls configured in the Vapi dashboard.
    """
    try:
        data = await request.json()
        message = data.get("message", {})

        # Check if this is a tool-call message
        if message.get("type") == "tool-calls":
            tool_calls = message.get("toolCallList", [])
            results = []

            for call in tool_calls:
                call_id = call.get("id")
                function_name = call.get("function", {}).get("name")
                arguments = call.get("function", {}).get("arguments", {})

                logger.info(f"Vapi called tool: {function_name} with args: {arguments}")

                result_content = ""

                if function_name == "query_knowledge_base":
                    query = arguments.get("query", "")
                    result_content = query_knowledge_base(query)

                elif function_name == "check_availability":
                    date_from = arguments.get("date_from")
                    date_to = arguments.get("date_to")
                    result_content = check_availability(date_from, date_to)

                elif function_name == "book_interview":
                    start_time = arguments.get("start_time")
                    name = arguments.get("name")
                    email = arguments.get("email")
                    result_content = book_interview(start_time, name, email)

                else:
                    result_content = f"Error: Function {function_name} not found."

                results.append({"toolCallId": call_id, "result": result_content})

            return {"results": results}

        return {"status": "ignored"}

    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
