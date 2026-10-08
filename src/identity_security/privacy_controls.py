import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

PRIVACY_FILE = (
    BASE_DIR / "data" / "privacy_settings.json"
)

LOG_FILE = (
    BASE_DIR / "logs" / "identity_security.log"
)


DEFAULT_PRIVACY = {
    "spatial_audio": False,
    "gesture_data": False,
    "behavioral_biometrics": False,
    "eye_tracking": False,
    "motion_tracking": False
}


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def load_privacy_database():
    if not PRIVACY_FILE.exists():
        return {"users": {}}

    with open(
        PRIVACY_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_privacy_database(database):
    PRIVACY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        PRIVACY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(database, file, indent=4)


def create_privacy_profile(user_id):
    database = load_privacy_database()

    if user_id not in database["users"]:
        database["users"][user_id] = (
            DEFAULT_PRIVACY.copy()
        )

        save_privacy_database(database)

    return database["users"][user_id]


def update_privacy_setting(
    user_id,
    data_type,
    allowed
):
    if data_type not in DEFAULT_PRIVACY:
        return {
            "status": "INVALID PRIVACY SETTING"
        }

    database = load_privacy_database()

    if user_id not in database["users"]:
        database["users"][user_id] = (
            DEFAULT_PRIVACY.copy()
        )

    database["users"][user_id][data_type] = bool(
        allowed
    )

    save_privacy_database(database)

    action = "ALLOWED" if allowed else "DENIED"

    write_log(
        f"PRIVACY_UPDATED | "
        f"user_id={user_id} | "
        f"data_type={data_type} | "
        f"access={action}"
    )

    return {
        "status": "PRIVACY SETTING UPDATED",
        "user_id": user_id,
        "data_type": data_type,
        "access": action
    }


def check_data_access(user_id, data_type):
    database = load_privacy_database()

    if user_id not in database["users"]:
        create_privacy_profile(user_id)
        database = load_privacy_database()

    allowed = database["users"][user_id].get(
        data_type,
        False
    )

    return {
        "user_id": user_id,
        "data_type": data_type,
        "access": (
            "ALLOWED"
            if allowed
            else "DENIED"
        )
    }


if __name__ == "__main__":

    user_id = "USER-DEMO-001"

    create_privacy_profile(user_id)

    update_privacy_setting(
        user_id,
        "spatial_audio",
        False
    )

    update_privacy_setting(
        user_id,
        "gesture_data",
        True
    )

    update_privacy_setting(
        user_id,
        "behavioral_biometrics",
        False
    )

    print("=" * 60)
    print("GameShield AI - Metaverse Privacy Controls")
    print("=" * 60)

    print("\nUser Privacy Decisions")
    print("-" * 60)

    for data_type in [
        "spatial_audio",
        "gesture_data",
        "behavioral_biometrics",
        "eye_tracking",
        "motion_tracking"
    ]:

        result = check_data_access(
            user_id,
            data_type
        )

        print(
            f"{data_type}: "
            f"{result['access']}"
        )