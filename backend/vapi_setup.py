import os
import requests
from prompts import SYSTEM_PROMPT

def create_or_update_vapi_agent():
    api_key = os.getenv("VAPI_PRIVATE_KEY")
    server_url = os.getenv("SERVER_URL") # E.g., https://your-railway-app.up.railway.app/vapi-webhook
    
    if not api_key:
        print("Error: VAPI_PRIVATE_KEY environment variable is not set.")
        return
        
    if not server_url:
        print("Warning: SERVER_URL is not set. The agent won't be able to call tools.")
        server_url = "http://localhost:8000/vapi-webhook"

    url = "https://api.vapi.ai/assistant"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": "Sanskar AI Persona",
        "model": {
            "provider": "google",
            "model": "gemini-2.5-flash",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "query_knowledge_base",
                        "description": "Queries Sanskar's resume and project READMEs to answer questions about his background, experience, and projects.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The specific question or topic to search for in the knowledge base."
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    "server": {
                        "url": server_url
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "check_availability",
                        "description": "Checks Sanskar's calendar for available interview slots.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date_from": {
                                    "type": "string",
                                    "description": "Start date in YYYY-MM-DD format. Optional."
                                },
                                "date_to": {
                                    "type": "string",
                                    "description": "End date in YYYY-MM-DD format. Optional."
                                }
                            }
                        }
                    },
                    "server": {
                        "url": server_url
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "book_interview",
                        "description": "Books an interview on Sanskar's calendar.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "start_time": {
                                    "type": "string",
                                    "description": "The ISO 8601 start time for the booking."
                                },
                                "name": {
                                    "type": "string",
                                    "description": "The name of the person booking the interview."
                                },
                                "email": {
                                    "type": "string",
                                    "description": "The email of the person booking the interview."
                                }
                            },
                            "required": ["start_time", "name", "email"]
                        }
                    },
                    "server": {
                        "url": server_url
                    }
                }
            ]
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "burt"
        },
        "firstMessage": "Hi, I'm the AI representation of Sanskar Dubey. I can answer any questions about his background, projects like VartaSync or TaskFlow AI, or we can go ahead and book an interview. How can I help you today?",
        "recordingEnabled": True
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Agent successfully created/updated! Agent ID: {data.get('id')}")
        print("Please link this Agent ID to your Twilio Phone Number in the Vapi Dashboard.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to create agent: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    create_or_update_vapi_agent()
