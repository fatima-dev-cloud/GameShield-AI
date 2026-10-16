
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

REPORT_FILE = (
    BASE_DIR / "reports" / "devsecops_dashboard.json"
)

CHECKS = [
    (
        "Python Automated Security Tests",
        [sys.executable, "-m", "pytest", "tests", "-q"]
    ),
    (
        "Bandit Static Security Scan",
        [sys.executable, "-m", "bandit", "-r", "src", "-ll"]
    ),
    (
        "Dependency Vulnerability Audit",
        [sys.executable, "-m", "pip_audit"]
    )
]


def main():
    results = []

    for title, command in CHECKS:
        print(f"\nRunning: {title}", flush=True)

        try:
            process = subprocess.run(
                command,
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )

            passed = process.returncode == 0

            results.append({
                "name": title,
                "status": "PASS" if passed else "FAIL",
                "exit_code": process.returncode
            })

            print(
                f"{title}: {'PASS' if passed else 'FAIL'}",
                flush=True
            )

        except subprocess.TimeoutExpired:
            results.append({
                "name": title,
                "status": "ERROR",
                "reason": "Check timed out"
            })

        except Exception as error:
            results.append({
                "name": title,
                "status": "ERROR",
                "reason": type(error).__name__
            })

    all_passed = all(
        result["status"] == "PASS"
        for result in results
    )

    report = {
        "platform": "GameShield AI",
        "module": "DevSecOps Security",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "overall_status": (
            "PASS" if all_passed else "FAIL"
        ),
        "checks": results
    }

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_FILE.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\nReport saved:")
    print(REPORT_FILE)

    print("\nOverall:", report["overall_status"])

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
