import json

DECISION_RULES = """
You are an automated pull request governance assistant.

Rules you MUST follow:
1. You do NOT decide scan success or failure.
2. You ONLY interpret provided scan results.
3. You MUST obey this mapping:
   - evaluation_outcome = PASS  -> decision = approve
   - evaluation_outcome = FAIL  -> decision = request_changes
   - evaluation_outcome = WAIT  -> decision = comment_only
4. You MUST return VALID JSON only.
5. Do NOT include markdown, explanations, or extra text.
"""

def build_prompt(policy: dict, scan_results: dict, evaluation_outcome: str) -> str:
    payload = {
        "policy": policy,
        "scan_results": scan_results,
        "evaluation_outcome": evaluation_outcome
    }

    return f"""
{DECISION_RULES}

Input:
{json.dumps(payload, indent=2)}

Output format (JSON only):
{{
  "decision": "approve | request_changes | comment_only",
  "comment": "clear explanation for developers"
}}
"""
