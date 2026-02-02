import requests
import json
import os
import sys

# Add project root to path to import settings if needed, 
# but for a standalone test script we can just read env or hardcode consistent with requirements.
# We will try to import settings.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.core.config import settings
    BASE_URL = settings.LLM_BASE_URL
    API_KEY = settings.LLM_API_KEY
    MODEL = settings.LLM_MODEL
except ImportError:
    # Fallback if run incorrectly
    print("Could not import settings, using defaults from .env (simulated)")
    BASE_URL = "http://localhost:1234/v1"
    API_KEY = "local-llm"
    MODEL = "openai-oss-20b"

def test_llm():
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        "temperature": 0.7
    }

    print(f"Testing LLM connection at: {url}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Connected to LLM")
            print("Response:", json.dumps(data, indent=2))
        else:
            print(f"FAILURE: Status Code {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(f"ERROR: Could not connect to LLM: {e}")

if __name__ == "__main__":
    test_llm()
