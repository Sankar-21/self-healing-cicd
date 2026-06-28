import time
import subprocess
import sys
import os

os.chdir("scripts")
sys.path.insert(0, ".")

def banner(text):
    print("\n" + "=" * 55)
    print(f"  {text}")
    print("=" * 55)

def step(n, text):
    print(f"\n[Step {n}] {text}")
    time.sleep(1)

banner("Self-Healing CI/CD Pipeline — Live Demo")

# Step 1: Show healthy state
step(1, "Checking current pipeline health...")
from failure_detector import detect
result = detect()

if not result:
    print("✅ Pipeline is healthy — no failures detected.")
else:
    print(f"⚠️  Active failure found: {result['category']}")

# Step 2: Simulate a failure classification
step(2, "Running ML classifier on sample log snippets...")
from rca_classifier import predict

samples = [
    "FAILED tests/test_main.py AssertionError assert 404 == 200",
    "ModuleNotFoundError: No module named 'fastapi'",
    "SyntaxError: invalid syntax line 5",
    "Connection refused localhost:8000 timeout",
    "401 Unauthorized invalid token github",
]

print(f"\n{'Log snippet':<45} {'Category':<22} {'Confidence'}")
print("-" * 80)
for s in samples:
    cat, conf = predict(s)
    print(f"{s[:44]:<45} {cat:<22} {conf}%")

# Step 3: Run full healer
step(3, "Running full self-healing cycle...")
from healer import run_healer
run_healer()

# Step 4: Summary
banner("Demo Complete")
print("""
  What was demonstrated:
  ✅ GitHub Actions CI pipeline (build + test)
  ✅ Automatic failure detection via GitHub API
  ✅ ML-based root cause classification (scikit-learn)
  ✅ Auto-remediation (retry / issue creation)
  ✅ React dashboard with live pipeline metrics
  ✅ Dockerized deployment
""")