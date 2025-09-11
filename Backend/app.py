# app.py

import os, json
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Create a FastAPI instance (our backend application)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3️⃣ Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (uses API key from environment variable)
client = OpenAI(api_key=api_key)

# Define the input schema for requests
# This ensures we receive JSON like: {"code": "some code here"}
class CodeInput(BaseModel):
    code: str

# Simple root endpoint (to check if backend is running)
@app.get("/")
def root():
    return {"message": "Backend is running!"}

# Main API endpoint: analyze code for bugs
@app.post("/analyze1")
def analyze_code1(input: CodeInput):
    # Send request to OpenAI model
    response = client.responses.create(
        model="gpt-4o-mini",  # Lightweight GPT model
        input=f"Analyze the following code for bugs and suggest fixes:\n\n{input.code}",
        store=True,
    )
    
    # Extract text output and return it as JSON
    return {"analysis": response.output_text}

@app.post("/analyze")
def analyze_code(input: CodeInput):
    messages=[
        {"role": "system", "content": "You are a code review assistant."},
        {"role": "user", "content": f"""
Analyze the following code and return ONLY a JSON object in this exact structure:

{{
  "errors": [
    {{"line": number, "description": "short explanation of the error"}}
  ],
  "fixes": [
    "suggestion to fix issue 1",
    "suggestion to fix issue 2"
  ],
  "summary": "2-3 sentence overall summary of the code",
  "functionality": [
    "key functionality point 1",
    "key functionality point 2"
  ],
  "conclusion": "short final remark about overall code quality"
}}

Rules:
- Always include the line numbers for each error (best estimate based on the code).
- Use concise descriptions.
- If there are no errors, return empty arrays for 'errors' and 'fixes'.
- Do NOT include any text outside of the JSON.

Code:
{input}
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Parse response safely
    try:
        analysis = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        analysis = {
            "summary": "Parsing failed",
            "raw": response.choices[0].message.content
        }

    return {"analysis": analysis}

# New endpoint to handle file uploads
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    code_text = content.decode("utf-8")  # assumes text file/code file

    # Call OpenAI to analyze code
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        # messages=[
        #     {"role": "system", "content": "You are a code review assistant."},
        #     {"role": "user", "content": f"Analyze this code:\n{code_text}"}
        # ]
        messages=[
            {"role": "system", "content": "You are a code review assistant."},
            {"role": "user", "content": f"""
Analyze this code and return JSON ONLY in this structure:

{{
  "summary": "2-3 sentence short summary",
  "functionality": ["point 1", "point 2", "point 3"],
  "errors": ["bug 1", "bug 2"],
  "improvements": ["suggestion 1", "suggestion 2"],
  "conclusion": "final thoughts in 1-2 sentences"
}}

Code:
{code_text}
            """}
        ]
    )

    # return {"filename": file.filename, "analysis": response.choices[0].message.content}
     # Try parsing JSON safely
    try:
        analysis = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        analysis = {"summary": "Parsing failed", "raw": response.choices[0].message.content}

    return {"filename": file.filename, "analysis": analysis}