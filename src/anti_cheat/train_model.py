from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "player_behavior.csv"
MODEL_FILE = BASE_DIR / "models" / "anti_cheat_model.joblib"

FEATURES = [
    "accuracy",
    "headshot_rate",
    "reaction_time",
    "kills_per_minute",
    "impossible_actions",
    "tracking_score",
]


def main():
    print("=" * 55)
    print("GameShield AI - Anti-Cheat Model Training")
    print("=" * 55)

    data = pd.read_csv(DATA_FILE)

    print(f"\nDataset loaded successfully: {len(data)} records")

    X = data[FEATURES]
    y = data["is_cheater"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )

    print("\nTraining Random Forest model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\nModel evaluation")
    print("-" * 55)
    print(f"Accuracy: {accuracy * 100:.2f}%")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=["Legitimate", "Cheater"],
            zero_division=0,
        )
    )

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    print(f"Model saved successfully:")
    print(MODEL_FILE)

    print("\nIMPORTANT:")
    print("This model uses synthetic demonstration data.")
    print("Its test accuracy is not a real-world anti-cheat benchmark.")


if __name__ == "__main__":
    main()