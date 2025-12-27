import os
import sys
import requests
import yaml

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# Load scan policy
with open(".ai/pr-scan-policy.yaml", "r") as f:
    policy = yaml.safe_load(f)

mandatory_checks = []
for checks in policy["mandatory_checks"].values():
    mandatory_checks.extend(checks)

# Fetch PR check runs
url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/commits"
commits = requests.get(url, headers=headers).json()
latest_commit = commits[-1]["sha"]

check_url = f"https://api.github.com/repos/{REPO}/commits/{latest_commit}/check-runs"
check_runs = requests.get(check_url, headers=headers).json()["check_runs"]

status_map = {c["name"]: c["conclusion"] for c in check_runs}

# Evaluate mandatory checks
wait, fail = False, False
for check in mandatory_checks:
    if check not in status_map or status_map[check] is None:
        wait = True
        break
    elif status_map[check] != "success":
        fail = True

if wait:
    print("WAIT")
    sys.exit(0)
elif fail:
    print("FAIL")
    sys.exit(1)
else:
    print("PASS")
    sys.exit(0)
