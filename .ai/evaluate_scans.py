import os
import sys
import json
import requests
import yaml

from watsonx_client import call_watsonx
from watsonx_prompt import build_prompt

# -----------------------------
# GitHub environment
# -----------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

if not all([GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_EVENT_PATH]):
    raise RuntimeError("Missing required GitHub environment variables")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# -----------------------------
# Watsonx environment
# -----------------------------
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_REGION = os.getenv("WATSONX_REGION")

if not all([WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_REGION]):
    raise RuntimeError("Missing required Watsonx environment variables")

# -----------------------------
# Load GitHub event
# -----------------------------
with open(GITHUB_EVENT_PATH, "r") as f:
    event = json.load(f)

pr_info = event.get("pull_request")
if pr_info is None:
    print("No pull_request found in event. Exiting.")
    sys.exit(0)

PR_NUMBER = pr_info["number"]

# -----------------------------
# Load scan policy
# -----------------------------
with open(".ai/pr-scan-policy.yaml", "r") as f:
    policy = yaml.safe_load(f)

mandatory_checks = []
for group in policy.get("mandatory_checks", {}).values():
    mandatory_checks.extend(group)

# -----------------------------
# Fetch latest commit SHA
# -----------------------------
commits_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}/commits"
commits_resp = requests.get(commits_url, headers=HEADERS)
commits_resp.raise_for_status()
latest_sha = commits_resp.json()[-1]["sha"]

# -----------------------------
# Fetch check runs
# -----------------------------
checks_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/commits/{latest_sha}/check-runs"
checks_resp = requests.get(checks_url, headers=HEADERS)
checks_resp.raise_for_status()
check_runs = checks_resp.json().get("check_runs", [])

status_map = {
    check["name"]: check["conclusion"]
    for check in check_runs
    if check["name"] != "evaluate-pr"
}

# -----------------------------
# DEBUG
# -----------------------------
print("Status map from GitHub API:")
for name, status in status_map.items():
    print(f"{name}: {status}")

# -----------------------------
# Evaluate mandatory checks
# -----------------------------
wait = False
fail = False

for check in mandatory_checks:
    if check not in status_map:
        print(f"Mandatory check missing: {check}")
        wait = True
        break
    if status_map[check] != "success":
        print(f"Mandatory check failed: {check}")
        fail = True

if wait:
    print("WAIT")
    sys.exit(0)

evaluation_outcome = "FAIL" if fail else "PASS"
print("Evaluation outcome:", evaluation_outcome)

# -----------------------------
# Prepare AI input (SINGLE SOURCE)
# -----------------------------
scan_results = {
    name: status
    for name, status in status_map.items()
    if name in mandatory_checks
}

prompt = build_prompt(
    policy=policy,
    scan_results=scan_results,
    evaluation_outcome=evaluation_outcome
)

if not prompt or not prompt.strip():
    raise RuntimeError("Generated Watsonx prompt is empty")

# -----------------------------
# Call Watsonx (TEXT MODEL)
# -----------------------------
ai_comment = call_watsonx(prompt).strip()

if not ai_comment:
    ai_comment = "All mandatory checks have passed. This pull request is ready for approval and merge."

# -----------------------------
# Log AI output
# -----------------------------
print("AI_COMMENT:")
print(ai_comment)
