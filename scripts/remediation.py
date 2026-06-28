import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO  = os.getenv("GITHUB_REPO")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ── Actions ──────────────────────────────────────────────

def retry_workflow(run_id):
    """Re-trigger all failed jobs in a run."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/rerun-failed-jobs"
    res = requests.post(url, headers=HEADERS)
    if res.status_code in (200, 201):
        print(f"🔁 Retried failed jobs for run {run_id}")
    else:
        print(f"⚠️  Retry failed: {res.status_code} - {res.text}")

def rollback_to_last_green():
    """Find last successful run and print its commit SHA for rollback reference."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?status=success&per_page=5"
    res = requests.get(url, headers=HEADERS)
    runs = res.json().get("workflow_runs", [])
    if not runs:
        print("⚠️  No successful runs found to rollback to.")
        return
    last_good = runs[0]
    sha     = last_good["head_sha"]
    html    = last_good["html_url"]
    print(f"⏪ Last green commit: {sha[:7]}")
    print(f"   Run URL: {html}")
    print(f"   To rollback: git revert HEAD or git reset --hard {sha[:7]}")

def notify_slack(category, run_url):
    """Send a Slack alert (optional — skip if no webhook set)."""
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        print("ℹ️  No SLACK_WEBHOOK_URL set — skipping notification.")
        return
    payload = {
        "text": f":rotating_light: *Pipeline failure detected*\n"
                f"Category: `{category}`\n"
                f"Run: {run_url}"
    }
    res = requests.post(webhook, json=payload)
    print(f"📣 Slack notified: {res.status_code}")

def create_github_issue(category, run_url):
    """Open a GitHub issue for failures that can't be auto-healed."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
    payload = {
        "title": f"[Auto-detected] Pipeline failure: {category}",
        "body": (
            f"## Pipeline failure report\n\n"
            f"**Category:** `{category}`\n"
            f"**Run URL:** {run_url}\n\n"
            f"This issue was automatically created by the self-healing CI/CD system.\n"
            f"Manual intervention required."
        ),
        "labels": ["bug", "ci-failure"]
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    if res.status_code == 201:
        print(f"🐛 GitHub issue created: {res.json()['html_url']}")
    else:
        print(f"⚠️  Issue creation failed: {res.status_code}")

# ── Remediation router ───────────────────────────────────

REMEDIATION_MAP = {
    "test_failure":       "retry",
    "infra_flap":         "retry",
    "dependency_missing": "issue",
    "build_error":        "issue",
    "auth_error":         "notify",
    "unknown":            "notify",
}

def remediate(run_id, category, run_url):
    print(f"\n🛠️  Starting remediation for category: {category}")
    action = REMEDIATION_MAP.get(category, "notify")

    if action == "retry":
        print("   Strategy: auto-retry failed jobs")
        retry_workflow(run_id)

    elif action == "rollback":
        print("   Strategy: rollback to last green")
        rollback_to_last_green()

    elif action == "issue":
        print("   Strategy: create GitHub issue for manual fix")
        notify_slack(category, run_url)
        create_github_issue(category, run_url)

    elif action == "notify":
        print("   Strategy: notify only")
        notify_slack(category, run_url)
        create_github_issue(category, run_url)

    print(f"\n✅ Remediation complete for run {run_id}")

if __name__ == "__main__":
    # Quick test with dummy values
    remediate(
        run_id=0,
        category="test_failure",
        run_url="https://github.com/Sankar-21/self-healing-cicd/actions"
    )