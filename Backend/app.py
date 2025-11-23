# app.py

import os, json, re
from fastapi import FastAPI, UploadFile, File, Form
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

@app.post("/analyze")
def analyze_code(input: CodeInput):

    code_text = input.code.strip()

    # 🔎 Simple heuristic: look for keywords or symbols
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "errorMsg": "⚠️ The input does not appear to be source code. Please paste a valid code snippet."
        }

    messages=[
        {"role": "system", "content": "You are a code review assistant."},
        {"role": "user", "content": f"""
Analyze the following code and return ONLY a JSON object in this exact structure:

{{
  "errors": [
    {{
      "line": <line_number>,                
      "description": "<short explanation>", 
      "code": "<exact code from that line>",
      "fix_suggestion": "<how to fix in words>",
      "corrected_code": "<corrected line or snippet>"
      "severity": "<Critical|Major|Minor>",
      "category": "<Runtime Error|Logic Error|Best Practice|Syntax Error>"
    }}
  ],
  "fixes": [
    {{
      "line": <line_number>,
      "suggestion": "<how to fix>",
      "corrected_code": "<corrected code line>"
    }}
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
    - Line numbers exactly match the provided code (count from 1).
    - The 'input' field contains the actual line text, escaped for JSON.
    - Use concise descriptions.
    - If there are no errors, return empty arrays for 'errors' and 'fixes'.
    - Do NOT include any text outside of the JSON.
    - Use one of the predefined severity and category labels.

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

    code_text = input.code.strip()

    # 🔎 Simple heuristic: look for keywords or symbols
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "message": "⚠️ The input does not appear to be source code. Please paste a valid code snippet."
        }
        
    messages=[
            {"role": "system", "content": "You are a code review assistant."},
            {"role": "user", "content": f"""
    Analyze the following code and return ONLY a JSON object in this exact structure:

    {{
    "errors": [
    {{
      "line": <line_number>,                
      "description": "<short explanation>", 
      "code": "<exact code from that line>",
      "fix_suggestion": "<how to fix in words>",
      "corrected_code": "<corrected line or snippet>",
      "severity": "<Critical|Major|Minor>",
      "category": "<Runtime Error|Logic Error|Best Practice|Syntax Error>"
    }}
  ],
    "fixes": [
    {{
      "line": <line_number>,
      "suggestion": "<how to fix>",
      "corrected_code": "<corrected code line>"
    }}
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
    - Line numbers exactly match the provided code (count from 1).
    - The 'input' field contains the actual line text, escaped for JSON.
    - Use concise descriptions.
    - If there are no errors, return empty arrays for 'errors' and 'fixes'.
    - Do NOT include any text outside of the JSON.
    - Use one of the predefined severity and category labels.

    Code:
    {input}
            """}
        ]

    # Call OpenAI to analyze code
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # return {"filename": file.filename, "analysis": response.choices[0].message.content}
     # Try parsing JSON safely
    try:
        analysis = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        analysis = {"summary": "Parsing failed", "raw": response.choices[0].message.content}

    return {"filename": file.filename, "analysis": analysis}

@app.post("/optimize")
def optimize_code(input: CodeInput):
    print("Received code for optimization:", input.code)
    code_text = input.code.strip()

    # simple validation like your /analyze
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "errorMsg": "⚠️ The input does not appear to be source code. Please paste a valid code snippet."
        }

    # prompt for GPT
    messages = [
        {"role": "system", "content": "You are a senior software engineer who specializes in writing clean, efficient, optimized code."},
        {"role": "user", "content": f"""
Optimize the following code and return ONLY a JSON object in this structure:

{{
  "optimized_code": "<optimized version of the input code>",
  "explanation": [
    "point 1: what was optimized",
    "point 2: why it improves efficiency",
    "point 3: effect on readability, performance, or complexity"
  ],
  "complexity_analysis": {{
    "before": "<estimated time/space complexity before optimization>",
    "after": "<estimated time/space complexity after optimization>"
  }},
  "remarks": "short summary of improvements"
}}

Rules:
- Focus on improving efficiency (time/space), readability, and maintainability.
- Preserve logic and output correctness.
- Always return valid JSON and no other text.
- Use bullet points in explanation.
- If no optimization possible, say so explicitly in 'remarks'.

Code:
{code_text}
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )

    try:
        optimization = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        optimization = {
            "optimized_code": "",
            "explanation": ["⚠️ Parsing failed"],
            "raw": response.choices[0].message.content
        }

    return {"optimization": optimization}

@app.post("/summarize")
def summarize_code(input: CodeInput):
    """
    Accepts JSON: { "code": "<...>" }
    Returns: { "summarization": { "summary": "...", "detailed_explanation": "...", "key_points": [...] } }
    """
    code_text = input.code.strip()

    # quick heuristic check (same as /analyze)
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "errorMsg": "⚠️ The input does not appear to be source code. Please paste a valid code snippet."
        }

    messages = [
        {"role": "system", "content": "You are an expert senior developer who writes concise, accurate code summaries."},
        {"role": "user", "content": f"""
Summarize the code below. Return ONLY a JSON object with this exact structure (no extra text):

{{
  "summary": "<one- to two-sentence high-level summary of what the code does>",
  "detailed_explanation": "<2-4 sentence explanation of how the code works, important functions and flow>",
  "key_points": [
    "bullet point 1",
    "bullet point 2",
    "bullet point 3"
  ]
}}

Rules:
- Keep JSON strictly valid.
- When you list key_points, keep them short (6-12 words each).
- Do NOT include examples or extra commentary outside the JSON.
- If code is too short or trivial, still return valid JSON with concise fields.

Code:
{code_text}
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        # return safe structure on parse failure
        result = {
            "summary": "",
            "detailed_explanation": "Parsing failed — model returned non-JSON output.",
            "key_points": [],
            "raw": response.choices[0].message.content
        }

    return {"summarization": result}


@app.post("/security-scan")
def scan_vulnerabilities(input: CodeInput):
    code_text = input.code.strip()

    # Quick validation
    if not code_text:
        return {"errorMsg": "No code provided."}

    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "errorMsg": "⚠️ The input does not appear to be source code. Please paste a valid code snippet."
        }
        
    messages = [
        {"role": "system", "content": "You are a cybersecurity code scanning assistant."},
        {"role": "user", "content": f"""
Scan the following code for **security vulnerabilities** and return ONLY JSON strictly in this structure:

{{
  "vulnerabilities": [
    {{
      "line": <line_number>,
      "description": "<short description of issue>",
      "vulnerability_type": "<SQL Injection | XSS | Hardcoded Secret | etc.>",
      "severity": "<Critical | High | Medium | Low>",
      "fix_suggestion": "<how to fix>"
    }}
  ],
  "summary": "Brief summary of the overall code security",
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ]
}}

Rules:
- If no vulnerabilities are found, return empty array for 'vulnerabilities'.
- Only return valid JSON (no extra text).
- Line numbers must correspond to provided code.
Code:
{code_text}
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        result = {
            "summary": "Parsing failed.",
            "raw": response.choices[0].message.content
        }

    return {"scan": result}

@app.post("/uploadFileToAnalyze")
async def upload_file_to_analyze(file: UploadFile = File(...)):
    import re, json
    from openai import OpenAI

    client = OpenAI()

    # ✅ Read uploaded file
    content = await file.read()
    code_text = content.decode("utf-8")

    # ✅ Detect if it looks like code
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "message": "⚠️ The uploaded file does not appear to contain source code."
        }

    # ✅ Build LLM prompt using the actual code
    messages = [
        {"role": "system", "content": "You are a code review assistant."},
        {"role": "user", "content": f"""
Analyze the following code and return ONLY a JSON object in this exact structure:

{{
  "errors": [
    {{
      "line": <line_number>,
      "description": "<short explanation>",
      "code": "<exact code from that line>",
      "fix_suggestion": "<how to fix in words>",
      "corrected_code": "<corrected line or snippet>",
      "severity": "<Critical|Major|Minor>",
      "category": "<Runtime Error|Logic Error|Best Practice|Syntax Error>"
    }}
  ],
  "fixes": [
    {{
      "line": <line_number>,
      "suggestion": "<how to fix>",
      "corrected_code": "<corrected code line>"
    }}
  ],
  "summary": "2-3 sentence overall summary of the code",
  "functionality": [
    "key functionality point 1",
    "key functionality point 2"
  ],
  "conclusion": "short final remark about overall code quality"
}}

Rules:
- Always include accurate line numbers.
- No text outside the JSON.
- If there are no errors, return empty arrays.

Code:
{code_text}
"""}
    ]

    # ✅ Call OpenAI (your model)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # ✅ Try parsing JSON returned by model
    try:
        analysis = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        analysis = {
            "summary": "⚠️ JSON parsing failed.",
            "raw": response.choices[0].message.content
        }

    return {
        "filename": file.filename,
        "analysis": analysis
    }

@app.post("/uploadFileToOptimize")
async def upload_file_to_optimize(file: UploadFile = File(...)):
    import re, json
    from openai import OpenAI

    client = OpenAI()

    # ✅ Read uploaded file
    content = await file.read()
    code_text = content.decode("utf-8")

    # ✅ Detect if it looks like code
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "message": "⚠️ The uploaded file does not appear to contain source code."
        }

    # ✅ Build LLM prompt using the actual code
    messages = [
        {"role": "system", "content": "You are a senior software engineer who specializes in writing clean, efficient, optimized code."},
        {"role": "user", "content": f"""
Optimize the following code and return ONLY a JSON object in this structure:

{{
  "optimized_code": "<optimized version of the input code>",
  "explanation": [
    "point 1: what was optimized",
    "point 2: why it improves efficiency",
    "point 3: effect on readability, performance, or complexity"
  ],
  "complexity_analysis": {{
    "before": "<estimated time/space complexity before optimization>",
    "after": "<estimated time/space complexity after optimization>"
  }},
  "remarks": "short summary of improvements"
}}

Rules:
- Focus on improving efficiency (time/space), readability, and maintainability.
- Preserve logic and output correctness.
- Always return valid JSON and no other text.
- Use bullet points in explanation.
- If no optimization possible, say so explicitly in 'remarks'.

Code:
{code_text}
        """}
    ]

    # ✅ Call OpenAI (your model)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # ✅ Try parsing JSON returned by model
    try:
        optimization = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        optimization = {
            "summary": "⚠️ JSON parsing failed.",
            "raw": response.choices[0].message.content
        }

    return {
        "filename": file.filename,
        "optimization": optimization
    }

@app.post("/uploadFileToSummarize")
async def upload_file_to_summarize(file: UploadFile = File(...)):
    import re, json
    from openai import OpenAI

    client = OpenAI()

    # ✅ Read uploaded file
    content = await file.read()
    code_text = content.decode("utf-8")

    # ✅ Detect if it looks like code
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "message": "⚠️ The uploaded file does not appear to contain source code."
        }

    # ✅ Build LLM prompt using the actual code
    messages = [
        {"role": "system", "content": "You are an expert senior developer who writes concise, accurate code summaries."},
        {"role": "user", "content": f"""
Summarize the code below. Return ONLY a JSON object with this exact structure (no extra text):

{{
  "summary": "<one- to two-sentence high-level summary of what the code does>",
  "detailed_explanation": "<2-4 sentence explanation of how the code works, important functions and flow>",
  "key_points": [
    "bullet point 1",
    "bullet point 2",
    "bullet point 3"
  ]
}}

Rules:
- Keep JSON strictly valid.
- When you list key_points, keep them short (6-12 words each).
- Do NOT include examples or extra commentary outside the JSON.
- If code is too short or trivial, still return valid JSON with concise fields.

Code:
{code_text}
        """}
    ]

    # ✅ Call OpenAI (your model)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # ✅ Try parsing JSON returned by model
    try:
        summarization = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        summarization = {
            "summary": "",
            "detailed_explanation": "Parsing failed — model returned non-JSON output.",
            "key_points": [],
            "raw": response.choices[0].message.content
        }

    return {
        "filename": file.filename,
        "summarization": summarization
    }

@app.post("/uploadFileToScan")
async def upload_file_to_scan(file: UploadFile = File(...)):
    import re, json
    from openai import OpenAI

    client = OpenAI()

    # ✅ Read uploaded file
    content = await file.read()
    code_text = content.decode("utf-8")

    # ✅ Detect if it looks like code
    code_pattern = re.compile(r"(class |def |public |function |\{|\};|;|\(|\))", re.MULTILINE)
    if not code_pattern.search(code_text):
        return {
            "errors": [],
            "message": "⚠️ The uploaded file does not appear to contain source code."
        }

    # ✅ Build LLM prompt using the actual code
    messages = [
        {"role": "system", "content": "You are a cybersecurity code scanning assistant."},
        {"role": "user", "content": f"""
Scan the following code for **security vulnerabilities** and return ONLY JSON strictly in this structure:

{{
  "vulnerabilities": [
    {{
      "line": <line_number>,
      "description": "<short description of issue>",
      "vulnerability_type": "<SQL Injection | XSS | Hardcoded Secret | etc.>",
      "severity": "<Critical | High | Medium | Low>",
      "fix_suggestion": "<how to fix>"
    }}
  ],
  "summary": "Brief summary of the overall code security",
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ]
}}

Rules:
- If no vulnerabilities are found, return empty array for 'vulnerabilities'.
- Only return valid JSON (no extra text).
- Line numbers must correspond to provided code.
Code:
{code_text}
        """}
    ]

    # ✅ Call OpenAI (your model)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # ✅ Try parsing JSON returned by model
    try:
        scan = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        scan = {
            "summary": "⚠️ JSON parsing failed.",
            "raw": response.choices[0].message.content
        }

    return {
        "filename": file.filename,
        "scan": scan
    }