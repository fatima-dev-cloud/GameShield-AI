from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "infrastructure_security.log"


GAME_RULES = {
    "max_movement_speed": 12.0,
    "max_damage_per_hit": 150,
    "max_fire_rate": 10.0
}


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def validate_game_action(action):
    violations = []

    movement_speed = float(
        action.get("movement_speed", 0)
    )

    damage = float(
        action.get("damage", 0)
    )

    fire_rate = float(
        action.get("fire_rate", 0)
    )

    if movement_speed > GAME_RULES["max_movement_speed"]:
        violations.append(
            "Impossible movement speed"
        )

    if damage > GAME_RULES["max_damage_per_hit"]:
        violations.append(
            "Invalid damage value"
        )

    if fire_rate > GAME_RULES["max_fire_rate"]:
        violations.append(
            "Impossible fire rate"
        )

    if violations:
        status = "ACTION REJECTED"

        write_log(
            f"SERVER_VALIDATION_FAILED | "
            f"player={action.get('player_id')} | "
            f"violations={'; '.join(violations)}"
        )

    else:
        status = "ACTION ACCEPTED"

        write_log(
            f"SERVER_VALIDATION_SUCCESS | "
            f"player={action.get('player_id')}"
        )

    return {
        "status": status,
        "valid": not violations,
        "violations": violations
    }


if __name__ == "__main__":
    print("=" * 60)
    print("GameShield AI - Server-Side Game Validation")
    print("=" * 60)

    suspicious_action = {
        "player_id": "PLAYER-9001",
        "movement_speed": 80,
        "damage": 999,
        "fire_rate": 30
    }

    result = validate_game_action(
        suspicious_action
    )

    print("\nValidation Result")
    print("-" * 60)
    print(f"Status: {result['status']}")
    print(f"Valid: {result['valid']}")

    print("\nDetected Violations:")

    for violation in result["violations"]:
        print(f"- {violation}")