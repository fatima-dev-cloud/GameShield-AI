
"""
GameShield AI - Cheating Category Detection

Educational rule-based detection for:
1. Aimbot-like behavior
2. Wallhack-like behavior
3. Automated cheating tools

Uses synthetic gameplay signals.
Results indicate suspicion, not proof of cheating.
"""

import math


def analyze_cheat_types(player_data):
    required_fields = [
        "accuracy",
        "headshot_rate",
        "reaction_time",
        "impossible_actions",
        "hidden_enemy_tracking_events",
        "repetitive_input_score",
    ]

    if not isinstance(player_data, dict):
        raise ValueError("Player data must be a JSON object")

    for field in required_fields:
        if field not in player_data:
            raise ValueError(f"Missing field: {field}")

    values = {}

    for field in required_fields:
        value = player_data[field]

        if isinstance(value, bool):
            raise ValueError(f"{field} must be numeric")

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                f"{field} must be a valid number"
            ) from None

        if not math.isfinite(number):
            raise ValueError(
                f"{field} must be a finite number"
            )

        values[field] = number

    for field in [
        "accuracy",
        "headshot_rate",
        "repetitive_input_score",
    ]:
        if not 0 <= values[field] <= 1:
            raise ValueError(
                f"{field} must be between 0 and 1"
            )

    if values["reaction_time"] < 0:
        raise ValueError(
            "reaction_time cannot be negative"
        )

    for field in [
        "impossible_actions",
        "hidden_enemy_tracking_events",
    ]:
        if values[field] < 0 or not values[field].is_integer():
            raise ValueError(
                f"{field} must be a non-negative integer"
            )

    detections = []

    # Aimbot-like indicators
    aimbot_signals = []

    if values["accuracy"] >= 0.95:
        aimbot_signals.append("EXTREME_ACCURACY")

    if values["headshot_rate"] >= 0.90:
        aimbot_signals.append("EXTREME_HEADSHOT_RATE")

    if values["reaction_time"] <= 80:
        aimbot_signals.append("UNUSUALLY_FAST_REACTION")

    if len(aimbot_signals) >= 2:
        detections.append({
            "cheat_type": "AIMBOT",
            "risk_level": "HIGH",
            "signals": aimbot_signals,
        })

    # Wallhack-like indicators
    if values["hidden_enemy_tracking_events"] >= 5:
        detections.append({
            "cheat_type": "WALLHACK",
            "risk_level": "HIGH",
            "signals": [
                "REPEATED_HIDDEN_ENEMY_TRACKING"
            ],
        })

    # Automated cheating indicators
    automation_signals = []

    if values["impossible_actions"] >= 5:
        automation_signals.append(
            "MULTIPLE_IMPOSSIBLE_ACTIONS"
        )

    if values["repetitive_input_score"] >= 0.90:
        automation_signals.append(
            "HIGHLY_REPETITIVE_INPUT_PATTERN"
        )

    if len(automation_signals) == 2:
        detections.append({
            "cheat_type": "AUTOMATED_CHEATING",
            "risk_level": "HIGH",
            "signals": automation_signals,
        })

    return {
        "module": "Cheating Category Detection",
        "suspicious": bool(detections),
        "detected_categories": [
            item["cheat_type"] for item in detections
        ],
        "detections": detections,
        "risk_level": "HIGH" if detections else "LOW",
        "note": (
            "Educational rule-based analysis of synthetic "
            "gameplay signals. Results are not proof of cheating."
        ),
    }


if __name__ == "__main__":
    scenarios = {
        "Legitimate Player": {
            "accuracy": 0.48,
            "headshot_rate": 0.22,
            "reaction_time": 280,
            "impossible_actions": 0,
            "hidden_enemy_tracking_events": 0,
            "repetitive_input_score": 0.20,
        },
        "Aimbot Example": {
            "accuracy": 0.98,
            "headshot_rate": 0.96,
            "reaction_time": 40,
            "impossible_actions": 0,
            "hidden_enemy_tracking_events": 0,
            "repetitive_input_score": 0.20,
        },
        "Wallhack Example": {
            "accuracy": 0.55,
            "headshot_rate": 0.30,
            "reaction_time": 220,
            "impossible_actions": 0,
            "hidden_enemy_tracking_events": 9,
            "repetitive_input_score": 0.20,
        },
        "Automated Cheating Example": {
            "accuracy": 0.65,
            "headshot_rate": 0.35,
            "reaction_time": 180,
            "impossible_actions": 12,
            "hidden_enemy_tracking_events": 0,
            "repetitive_input_score": 0.98,
        },
    }

    for name, activity in scenarios.items():
        result = analyze_cheat_types(activity)

        print("\n" + "=" * 55)
        print(name)
        print("=" * 55)
        print("Risk Level:", result["risk_level"])
        print("Suspicious:", result["suspicious"])
        print(
            "Detected Categories:",
            result["detected_categories"]
        )