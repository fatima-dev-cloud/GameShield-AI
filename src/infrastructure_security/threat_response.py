from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "infrastructure_security.log"


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def respond_to_threat(threat_type, severity, source):
    severity = severity.upper()

    if severity == "CRITICAL":
        action = "BLOCK SOURCE AND ISOLATE SESSION"

    elif severity == "HIGH":
        action = "TEMPORARILY BLOCK SOURCE"

    elif severity == "MEDIUM":
        action = "RATE LIMIT AND MONITOR"

    else:
        action = "LOG AND MONITOR"

    result = {
        "threat_type": threat_type,
        "severity": severity,
        "source": source,
        "automated_action": action
    }

    write_log(
        f"THREAT_RESPONSE | "
        f"type={threat_type} | "
        f"severity={severity} | "
        f"source={source} | "
        f"action={action}"
    )

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("GameShield AI - Automated Threat Response")
    print("=" * 60)

    threats = [
        {
            "type": "Abnormal Request Flood",
            "severity": "HIGH",
            "source": "CLIENT-ATTACKER-01"
        },
        {
            "type": "Game Packet Tampering",
            "severity": "CRITICAL",
            "source": "PLAYER-ATTACKER-02"
        },
        {
            "type": "Suspicious Traffic Pattern",
            "severity": "MEDIUM",
            "source": "CLIENT-UNKNOWN-03"
        }
    ]

    for threat in threats:
        result = respond_to_threat(
            threat["type"],
            threat["severity"],
            threat["source"]
        )

        print("\nThreat Detected")
        print("-" * 60)
        print(f"Type: {result['threat_type']}")
        print(f"Severity: {result['severity']}")
        print(f"Source: {result['source']}")
        print(
            f"Automated Action: "
            f"{result['automated_action']}"
        )