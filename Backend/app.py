# app.py

import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a FastAPI instance (our backend application)
app = FastAPI()

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
@app.post("/analyze")
def analyze_code(input: CodeInput):
    # Send request to OpenAI model
    response = client.responses.create(
        model="gpt-4o-mini",  # Lightweight GPT model
        input=f"Analyze the following code for bugs and suggest fixes:\n\n{input.code}",
        store=True,
    )
    
    # Extract text output and return it as JSON
    return {"analysis": response.output_text}