import os
import requests
import json

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
REGION = os.getenv("WATSONX_REGION")

if not all([API_KEY, PROJECT_ID, REGION]):
    raise RuntimeError("Missing required Watsonx environment variables")

URL = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/chat/completions?version=2024-03-01"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def call_watsonx(prompt: str) -> str:
    payload = {
        "model": "meta-llama/llama-3-70b-instruct",
        "project_id": PROJECT_ID,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI PR reviewer enforcing repository policy."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2
    }

    response = requests.post(URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]
