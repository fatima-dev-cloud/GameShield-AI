from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_FILE = BASE_DIR / "models" / "anti_cheat_model.joblib"
LOG_FILE = BASE_DIR / "logs" / "anti_cheat.log"

FEATURES = [
    "accuracy",
    "headshot_rate",
    "reaction_time",
    "kills_per_minute",
    "impossible_actions",
    "tracking_score",
]


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Anti-cheat model not found. Run train_model.py first."
        )

    return joblib.load(MODEL_FILE)


def analyze_player(player_data):
    model = load_model()

    player_frame = pd.DataFrame(
        [[player_data[feature] for feature in FEATURES]],
        columns=FEATURES,
    )

    prediction = int(model.predict(player_frame)[0])

    probabilities = model.predict_proba(player_frame)[0]
    class_probabilities = dict(zip(model.classes_, probabilities))

    cheat_probability = float(class_probabilities.get(1, 0.0))

    if cheat_probability >= 0.80:
        risk_level = "HIGH"
    elif cheat_probability >= 0.50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    result = {
        "prediction": prediction,
        "status": "CHEATER DETECTED" if prediction == 1 else "LEGIT PLAYER",
        "risk_level": risk_level,
        "cheat_probability": round(cheat_probability * 100, 2),
    }

    write_security_log(player_data, result)

    return result


def write_security_log(player_data, result):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="seconds")

    log_message = (
        f"{timestamp} | "
        f"accuracy={player_data['accuracy']} | "
        f"headshot_rate={player_data['headshot_rate']} | "
        f"reaction_time={player_data['reaction_time']} | "
        f"kills_per_minute={player_data['kills_per_minute']} | "
        f"impossible_actions={player_data['impossible_actions']} | "
        f"tracking_score={player_data['tracking_score']} | "
        f"status={result['status']} | "
        f"risk={result['risk_level']} | "
        f"cheat_probability={result['cheat_probability']}%\n"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_message)


if __name__ == "__main__":
    test_player = {
         "accuracy": 0.47,
         "headshot_rate": 0.21,
         "reaction_time": 290,
         "kills_per_minute": 1.5,
         "impossible_actions": 0,
         "tracking_score": 0.39,
}

    result = analyze_player(test_player)

    print("=" * 55)
    print("GameShield AI - Player Security Analysis")
    print("=" * 55)

    print("\nPlayer behavior:")
    for key, value in test_player.items():
        print(f"{key}: {value}")

    print("\nSecurity Result")
    print("-" * 55)
    print(f"Status: {result['status']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Cheat Probability: {result['cheat_probability']}%")