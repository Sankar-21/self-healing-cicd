from failure_detector import detect
from remediation import remediate
import time

def run_healer():
    print("=" * 50)
    print("  Self-Healing CI/CD — Healer Started")
    print("=" * 50)

    result = detect()

    if result:
        remediate(
            run_id=result["run_id"],
            category=result["category"],
            run_url=result["url"]
        )
    else:
        print("✅ No failures detected. Pipeline is healthy.")

if __name__ == "__main__":
    run_healer()