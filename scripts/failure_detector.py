import os
import re
import requests
from dotenv import load_dotenv
from rca_classifier import predict
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO  = os.getenv("GITHUB_REPO")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Failure patterns → category mapping
FAILURE_PATTERNS = [
    (r"ModuleNotFoundError|No module named",     "dependency_missing"),
    (r"FAILED tests/|AssertionError",            "test_failure"),
    (r"SyntaxError|IndentationError",            "build_error"),
    (r"Connection refused|timeout|unavailable",  "infra_flap"),
    (r"permission denied|403|401",               "auth_error"),
]

def get_latest_failed_run():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?status=failure&per_page=5"
    res = requests.get(url, headers=HEADERS)
    runs = res.json().get("workflow_runs", [])
    if not runs:
        print("No failed runs found.")
        return None
    return runs[0]  # most recent failure

def get_run_logs(run_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/logs"
    try:
        res = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        if res.status_code == 302 or res.url != url:
            log_res = requests.get(res.url, timeout=10)
            return log_res.text
        return res.text
    except requests.exceptions.Timeout:
        print("⚠️  Log fetch timed out — using run metadata for classification.")
        return f"run {run_id} failed"
    except Exception as e:
        print(f"⚠️  Log fetch error: {e}")
        return f"run {run_id} failed"

def classify_failure(log_text):
    category, confidence = predict(log_text)
    print(f"🧠 ML confidence: {confidence}%")
    return category

def detect():
    print("🔍 Checking for failed pipeline runs...")
    run = get_latest_failed_run()
    if not run:
        return

    run_id   = run["id"]
    run_name = run["name"]
    html_url = run["html_url"]

    print(f"❌ Failed run: {run_name} (ID: {run_id})")
    print(f"   URL: {html_url}")

    log_text = get_run_logs(run_id)
    category = classify_failure(log_text)

    print(f"📂 Failure category: {category}")
    return {"run_id": run_id, "category": category, "url": html_url}

if __name__ == "__main__":
    detect()