import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from google import genai

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_DIR = BASE_DIR / "resume"
READMES_DIR = BASE_DIR / "readmes"
CHROMA_PERSIST_DIR = BASE_DIR / "backend" / "chroma_db"


class GeminiEmbeddings(Embeddings):
    """Custom Langchain-compatible wrapper around the google-genai SDK."""

    def __init__(self, model: str = "gemini-embedding-001"):
        self.model = model
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=api_key)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import time
        all_embeddings = []
        # Very small batches + generous delay to respect free-tier rate limits (100 req/min)
        batch_size = 2
        total_batches = (len(texts) + batch_size - 1) // batch_size
        for i in range(0, len(texts), batch_size):
            batch_num = i // batch_size + 1
            batch = texts[i : i + batch_size]
            for attempt in range(5):
                try:
                    result = self.client.models.embed_content(
                        model=self.model,
                        contents=batch,
                    )
                    all_embeddings.extend([e.values for e in result.embeddings])
                    print(f"  Embedded batch {batch_num}/{total_batches}")
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < 4:
                        wait_time = (attempt + 1) * 15
                        print(f"  Rate limited on batch {batch_num}, waiting {wait_time}s... (attempt {attempt+1}/5)")
                        time.sleep(wait_time)
                    else:
                        raise
            # Delay between batches to stay under 100 req/min
            time.sleep(2)
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        import time
        for attempt in range(5):
            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=[text],
                )
                return result.embeddings[0].values
            except Exception as e:
                if "429" in str(e) and attempt < 4:
                    wait_time = (attempt + 1) * 5
                    print(f"  Rate limited on query embed, waiting {wait_time}s... (attempt {attempt+1}/5)")
                    time.sleep(wait_time)
                else:
                    raise


def get_embeddings():
    return GeminiEmbeddings()


def load_documents():
    documents = []

    # Load Resume PDF
    for pdf_file in RESUME_DIR.glob("*.pdf"):
        try:
            loader = PyPDFLoader(str(pdf_file))
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    # Load READMEs (Markdown)
    for md_file in READMES_DIR.glob("*.md"):
        try:
            loader = TextLoader(str(md_file), encoding="utf-8")
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {md_file}: {e}")

    return documents


def build_or_load_vector_store():
    embeddings = get_embeddings()

    # If the database already exists, load it
    if CHROMA_PERSIST_DIR.exists() and any(CHROMA_PERSIST_DIR.iterdir()):
        print("Loading existing Chroma database...")
        vector_store = Chroma(
            persist_directory=str(CHROMA_PERSIST_DIR),
            embedding_function=embeddings,
        )
        return vector_store

    print("Building new Chroma database...")
    documents = load_documents()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_PERSIST_DIR),
    )
    vector_store.persist()
    print("Database built and persisted successfully.")

    return vector_store


def query_knowledge_base(query: str, k: int = 4) -> str:
    """
    Queries the vector database and returns a combined string of context.
    """
    vector_store = build_or_load_vector_store()
    results = vector_store.similarity_search(query, k=k)

    if not results:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for doc in results:
        source = doc.metadata.get("source", "Unknown Source")
        filename = Path(source).name if source else "Unknown"
        context_parts.append(f"--- From {filename} ---\n{doc.page_content}")

    return "\n\n".join(context_parts)


if __name__ == "__main__":
    build_or_load_vector_store()
    print("---\nTest Query:")
    result = query_knowledge_base("What is your experience with RAG?")
    print(result.encode("utf-8", errors="replace").decode("utf-8"))
