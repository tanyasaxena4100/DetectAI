import os
import requests
import json

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
REGION = os.getenv("WATSONX_REGION")

if not all([API_KEY, PROJECT_ID, REGION]):
    raise RuntimeError("Missing required Watsonx environment variables")


def get_iam_token() -> str:
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": API_KEY
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def call_watsonx(prompt: str) -> str:
    access_token = get_iam_token()

    # url = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/chat?version=2024-03-01"
    url = f"{WATSONX_URL}/ml/v1/chat/completions?version=2024-03-01"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": "ibm/granite-13b-chat-v2",
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
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.2
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("===== WATSONX DEBUG =====")
        print("Watsonx URL:", url)
        print("Status code:", response.status_code)
        print("Response body:", response.text)
        print("========================")
        response.raise_for_status()
    
    result = response.json()
    return result["results"][0]["generated_text"]
