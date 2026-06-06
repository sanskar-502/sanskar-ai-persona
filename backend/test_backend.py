import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("--- Testing /health ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Error: {e}\n")

def test_chat():
    print("--- Testing /chat ---")
    payload = {
        "messages": [
            {"role": "user", "content": "What is your experience with RAG pipelines? Answer in 2 sentences."}
        ]
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Error: {e}\n")

def test_webhook_query():
    print("--- Testing /vapi-webhook (query_knowledge_base) ---")
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "query_knowledge_base",
                        "arguments": {"query": "Tell me about the VartaSync project."}
                    }
                }
            ]
        }
    }
    try:
        response = requests.post(f"{BASE_URL}/vapi-webhook", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

def test_webhook_calendar():
    print("--- Testing /vapi-webhook (check_availability) ---")
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "call_456",
                    "function": {
                        "name": "check_availability",
                        "arguments": {}
                    }
                }
            ]
        }
    }
    try:
        response = requests.post(f"{BASE_URL}/vapi-webhook", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == "__main__":
    test_health()
    test_chat()
    test_webhook_query()
    test_webhook_calendar()
