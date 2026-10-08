from datetime import datetime, timezone
from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    BASE_DIR / "models" / "content_moderation_model.joblib"
)

LOG_FILE = (
    BASE_DIR / "logs" / "content_moderation.log"
)


def write_moderation_log(message):
    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            f"{timestamp} | {message}\n"
        )


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Content moderation model not found. "
            "Run train_moderation_model.py first."
        )

    return joblib.load(MODEL_FILE)


def moderate_text(text):
    model = load_model()

    clean_text = str(text).strip()

    if not clean_text:
        return {
            "status": "REJECTED",
            "action": "BLOCK",
            "reason": "Empty message",
            "toxicity_probability": 0.0
        }

    prediction = int(
        model.predict([clean_text])[0]
    )

    probabilities = (
        model.predict_proba([clean_text])[0]
    )

    class_probabilities = dict(
        zip(
            model.classes_,
            probabilities
        )
    )

    toxicity_probability = float(
        class_probabilities.get(1, 0.0)
    )

    if toxicity_probability >= 0.70:
        risk_level = "HIGH"
    elif toxicity_probability >= 0.45:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if prediction == 1:
        status = "TOXIC CONTENT DETECTED"
        action = "BLOCK"
    else:
        status = "CONTENT SAFE"
        action = "ALLOW"

    result = {
        "status": status,
        "action": action,
        "risk_level": risk_level,
        "toxicity_probability": round(
            toxicity_probability * 100,
            2
        )
    }

    write_moderation_log(
        f"TEXT_MODERATION | "
        f"status={status} | "
        f"action={action} | "
        f"risk={risk_level} | "
        f"toxicity={result['toxicity_probability']}%"
    )

    return result


if __name__ == "__main__":

    messages = [
        "good game everyone",
        "shut up idiot"
    ]

    print("=" * 60)
    print("GameShield AI - AI Content Moderation")
    print("=" * 60)

    for message in messages:
        result = moderate_text(message)

        print("\nMessage Analysis")
        print("-" * 60)
        print(f"Message: {message}")
        print(f"Status: {result['status']}")
        print(f"Action: {result['action']}")
        print(
            f"Risk Level: "
            f"{result['risk_level']}"
        )
        print(
            f"Toxicity Probability: "
            f"{result['toxicity_probability']}%"
        )