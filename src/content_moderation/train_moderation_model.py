from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR / "data" / "moderation_dataset.csv"
)

MODEL_FILE = (
    BASE_DIR / "models" / "content_moderation_model.joblib"
)


def main():
    print("=" * 60)
    print("GameShield AI - Content Moderation Model Training")
    print("=" * 60)

    data = pd.read_csv(DATA_FILE)

    print(
        f"\nDataset loaded successfully: "
        f"{len(data)} messages"
    )

    X = data["text"]
    y = data["is_toxic"]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.30,
            random_state=42,
            stratify=y
        )
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2)
            )
        ),
        (
            "classifier",
            LogisticRegression(
                random_state=42
            )
        )
    ])

    print("\nTraining NLP toxicity classifier...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\nModel Evaluation")
    print("-" * 60)

    print(
        f"Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Safe",
                "Toxic"
            ],
            zero_division=0
        )
    )

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print("\nModel saved successfully:")
    print(MODEL_FILE)

    print("\nIMPORTANT:")
    print(
        "This model uses a small synthetic "
        "demonstration dataset."
    )
    print(
        "Its accuracy is not a production "
        "moderation benchmark."
    )


if __name__ == "__main__":
    main()