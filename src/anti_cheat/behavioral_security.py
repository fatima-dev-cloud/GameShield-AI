
"""
GameShield AI - Behavioral Account Security

Educational detection of suspicious account sharing
and rank boosting based on synthetic activity signals.

Results indicate risk, not proof of misconduct.
"""


def detect_account_sharing(activity):
    required = [
        "distance_km",
        "time_difference_minutes",
        "device_changed",
        "behavior_change_score",
    ]

    for field in required:
        if field not in activity:
            raise ValueError(f"Missing field: {field}")

    distance = float(activity["distance_km"])
    minutes = float(activity["time_difference_minutes"])
    behavior = float(activity["behavior_change_score"])

    if distance < 0 or minutes < 0:
        raise ValueError("Distance and time cannot be negative")

    if not 0 <= behavior <= 1:
        raise ValueError(
            "behavior_change_score must be between 0 and 1"
        )

    if not isinstance(activity["device_changed"], bool):
        raise ValueError("device_changed must be a boolean")

    signals = []

    # Unusually distant logins in a short time window.
    if distance >= 1000 and minutes <= 60:
        signals.append("IMPOSSIBLE_TRAVEL")

    if activity["device_changed"]:
        signals.append("NEW_DEVICE")

    if behavior >= 0.75:
        signals.append("MAJOR_BEHAVIOR_CHANGE")

    risk_score = 0

    if "IMPOSSIBLE_TRAVEL" in signals:
        risk_score += 50

    if "NEW_DEVICE" in signals:
        risk_score += 20

    if "MAJOR_BEHAVIOR_CHANGE" in signals:
        risk_score += 30

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "module": "Account Sharing Detection",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "suspicious": risk_score >= 70,
        "signals": signals,
        "note": (
            "Risk indicators are not proof of account sharing. "
            "VPNs, travel and legitimate device changes may "
            "cause false positives."
        ),
    }


def detect_rank_boosting(activity):
    required = [
        "previous_win_rate",
        "current_win_rate",
        "rank_increase",
        "matches_played",
        "performance_change_score",
    ]

    for field in required:
        if field not in activity:
            raise ValueError(f"Missing field: {field}")

    previous = float(activity["previous_win_rate"])
    current = float(activity["current_win_rate"])
    rank_increase = int(activity["rank_increase"])
    matches = int(activity["matches_played"])
    performance = float(activity["performance_change_score"])

    if not 0 <= previous <= 1 or not 0 <= current <= 1:
        raise ValueError("Win rates must be between 0 and 1")

    if rank_increase < 0 or matches < 0:
        raise ValueError(
            "Rank increase and matches cannot be negative"
        )

    if not 0 <= performance <= 1:
        raise ValueError(
            "performance_change_score must be between 0 and 1"
        )

    signals = []

    if current - previous >= 0.40:
        signals.append("SUDDEN_WIN_RATE_INCREASE")

    if rank_increase >= 5 and matches <= 10:
        signals.append("UNUSUAL_RANK_PROGRESS")

    if performance >= 0.75:
        signals.append("MAJOR_PERFORMANCE_CHANGE")

    risk_score = 0

    if "SUDDEN_WIN_RATE_INCREASE" in signals:
        risk_score += 35

    if "UNUSUAL_RANK_PROGRESS" in signals:
        risk_score += 40

    if "MAJOR_PERFORMANCE_CHANGE" in signals:
        risk_score += 25

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "module": "Rank Boosting Detection",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "suspicious": risk_score >= 70,
        "signals": signals,
        "note": (
            "Unusual performance is not proof of boosting. "
            "Skill improvement and matchmaking differences "
            "can produce similar patterns."
        ),
    }


if __name__ == "__main__":
    sharing_demo = {
        "distance_km": 5000,
        "time_difference_minutes": 20,
        "device_changed": True,
        "behavior_change_score": 0.90,
    }

    boosting_demo = {
        "previous_win_rate": 0.35,
        "current_win_rate": 0.90,
        "rank_increase": 7,
        "matches_played": 8,
        "performance_change_score": 0.85,
    }

    print("=== ACCOUNT SHARING DEMO ===")
    print(detect_account_sharing(sharing_demo))

    print("\n=== RANK BOOSTING DEMO ===")
    print(detect_rank_boosting(boosting_demo))