import os
import sys
import json
import requests
import yaml

from watsonx_client import call_watsonx
from watsonx_prompt import build_prompt


# -----------------------------
# Environment & constants
# -----------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

if not all([GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_EVENT_PATH]):
    raise RuntimeError("Missing required GitHub environment variables")

# -----------------------------
# Watsonx environment
# -----------------------------
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_REGION = os.getenv("WATSONX_REGION")

if not all([WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_REGION]):
    raise RuntimeError("Missing required Watsonx environment variables")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# -----------------------------
# Load GitHub event
# -----------------------------
with open(GITHUB_EVENT_PATH, "r") as f:
    event = json.load(f)

if "pull_request" not in event:
    print("No pull request context found. Exiting.")
    sys.exit(0)

PR_NUMBER = event["pull_request"]["number"]


# -----------------------------
# Load scan policy
# -----------------------------
with open(".ai/pr-scan-policy.yaml", "r") as f:
    policy = yaml.safe_load(f)

mandatory_checks = []
for group in policy["mandatory_checks"].values():
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
}


# -----------------------------
# Evaluate mandatory checks
# -----------------------------
wait = False
fail = False

for check in mandatory_checks:
    if check not in status_map:
        wait = True
        break

    if status_map[check] is None:
        wait = True
        break

    if status_map[check] != "success":
        fail = True


if wait:
    print("WAIT")
    sys.exit(0)

evaluation_outcome = "FAIL" if fail else "PASS"
print(evaluation_outcome)


# -----------------------------
# Prepare AI input
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


# -----------------------------
# Call Watsonx
# -----------------------------
raw_response = call_watsonx(prompt)

try:
    ai_result = json.loads(raw_response)
except json.JSONDecodeError:
    raise RuntimeError("Watsonx returned invalid JSON")

decision = ai_result.get("decision")
comment = ai_result.get("comment")


# -----------------------------
# Log AI decision (no side effects yet)
# -----------------------------
print("AI_DECISION:", decision)
print("AI_COMMENT:", comment)
