from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

LOG_FILE = (
    BASE_DIR / "logs" / "content_moderation.log"
)


CONTENT_RATINGS = {
    "EVERYONE": 0,
    "TEEN": 13,
    "MATURE": 17,
    "ADULT": 18
}


def write_log(message):
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


def check_age_appropriate_content(
    user_age,
    content_rating
):
    user_age = int(user_age)

    rating = str(
        content_rating
    ).upper()

    if rating not in CONTENT_RATINGS:
        return {
            "status": "INVALID CONTENT RATING",
            "access": "DENIED"
        }

    minimum_age = CONTENT_RATINGS[rating]

    if user_age >= minimum_age:
        access = "ALLOWED"
        status = "AGE-APPROPRIATE CONTENT"
    else:
        access = "BLOCKED"
        status = "CHILD SAFETY FILTER TRIGGERED"

    result = {
        "user_age": user_age,
        "content_rating": rating,
        "minimum_age": minimum_age,
        "status": status,
        "access": access
    }

    write_log(
        f"CHILD_SAFETY | "
        f"age={user_age} | "
        f"rating={rating} | "
        f"access={access}"
    )

    return result


if __name__ == "__main__":

    print("=" * 60)
    print("GameShield AI - Child Safety Controls")
    print("=" * 60)

    tests = [
        {
            "age": 12,
            "rating": "EVERYONE"
        },
        {
            "age": 12,
            "rating": "TEEN"
        },
        {
            "age": 15,
            "rating": "MATURE"
        },
        {
            "age": 18,
            "rating": "MATURE"
        }
    ]

    for test in tests:
        result = check_age_appropriate_content(
            test["age"],
            test["rating"]
        )

        print("\nContent Access Check")
        print("-" * 60)
        print(
            f"User Age: "
            f"{result['user_age']}"
        )
        print(
            f"Content Rating: "
            f"{result['content_rating']}"
        )
        print(
            f"Minimum Age: "
            f"{result['minimum_age']}"
        )
        print(
            f"Status: "
            f"{result['status']}"
        )
        print(
            f"Access: "
            f"{result['access']}"
        )