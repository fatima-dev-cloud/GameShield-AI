import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def run_step(title, command):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        check=False,
    )

    if result.returncode == 0:
        print(f"\nPASS: {title}")
        return True

    print(f"\nFAIL: {title}")
    return False


def main():
    checks = [
        (
            "Python Automated Security Tests",
            [
                sys.executable,
                "-m",
                "pytest",
                "tests",
                "-v",
            ],
        ),
        (
            "Bandit Static Security Scan",
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                "src",
                "-ll",
            ],
        ),
        (
            "Dependency Vulnerability Audit",
            [
                sys.executable,
                "-m",
                "pip_audit",
            ],
        ),
    ]

    results = []

    for title, command in checks:
        passed = run_step(title, command)
        results.append((title, passed))

    print("\n" + "=" * 60)
    print("GameShield AI - DevSecOps Security Report")
    print("=" * 60)

    for title, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{title}: {status}")

    all_passed = all(
        passed for _, passed in results
    )

    print("\nFinal Result:")

    if all_passed:
        print("ALL SECURITY CHECKS PASSED")
        return 0

    print("SECURITY PIPELINE FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())