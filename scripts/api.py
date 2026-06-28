from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, os, re, joblib
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO  = os.getenv("GITHUB_REPO")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rca_model.pkl")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def classify(log_text):
    if not os.path.exists(MODEL_PATH):
        return "unknown", 0.0
    model = joblib.load(MODEL_PATH)
    category   = model.predict([log_text])[0]
    proba      = model.predict_proba([log_text])[0]
    confidence = round(max(proba) * 100, 1)
    return category, confidence

@app.get("/api/runs")
def get_runs():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page=10"
    res = requests.get(url, headers=HEADERS)
    runs = res.json().get("workflow_runs", [])

    result = []
    for run in runs:
        category   = "unknown"
        confidence = 0.0

        if run["conclusion"] == "failure":
            # Use a sample log snippet for classification
            log_snippet = f"Run {run['id']} failed at {run['updated_at']}"
            category, confidence = classify(log_snippet)

        result.append({
            "id":         run["id"],
            "name":       run["display_title"],
            "status":     run["conclusion"] or "running",
            "branch":     run["head_branch"],
            "commit":     run["head_sha"][:7],
            "url":        run["html_url"],
            "updated_at": run["updated_at"],
            "category":   category,
            "confidence": confidence,
        })

    return result

@app.get("/api/stats")
def get_stats():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page=20"
    res = requests.get(url, headers=HEADERS)
    runs = res.json().get("workflow_runs", [])

    total    = len(runs)
    success  = sum(1 for r in runs if r["conclusion"] == "success")
    failed   = sum(1 for r in runs if r["conclusion"] == "failure")
    running  = sum(1 for r in runs if r["conclusion"] is None)

    return {
        "total":       total,
        "success":     success,
        "failed":      failed,
        "running":     running,
        "health_rate": round((success / total * 100) if total else 0, 1)
    }