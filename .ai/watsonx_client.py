import os
import requests

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_REGION = os.getenv("WATSONX_REGION", "us-south")

if not all([WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_REGION]):
    raise RuntimeError("Missing required Watsonx environment variables")

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
WATSONX_API_BASE = f"https://{WATSONX_REGION}.ml.cloud.ibm.com"


def _get_iam_token():
    response = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": WATSONX_API_KEY,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def call_watsonx(prompt: str) -> dict:
    token = _get_iam_token()

    url = f"{WATSONX_API_BASE}/ml/v1/text/generation?version=2024-03-01"

    payload = {
        "model_id": "ibm/granite-13b-chat-v2",
        "project_id": WATSONX_PROJECT_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 300,
            "temperature": 0.2
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    result = response.json()
    return result["results"][0]["generated_text"]
