import json
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet


BASE_DIR = Path(__file__).resolve().parents[2]

KEY_FILE = BASE_DIR / "config" / "biometric.key"

ENCRYPTED_DATA_FILE = (
    BASE_DIR / "data" / "protected_biometrics.dat"
)

LOG_FILE = (
    BASE_DIR / "logs" / "identity_security.log"
)


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def load_or_create_key():
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)

    return key


def encrypt_biometric_data(user_id, biometric_data):
    key = load_or_create_key()
    cipher = Fernet(key)

    protected_record = {
        "user_id": user_id,
        "recorded_at": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "biometric_data": biometric_data
    }

    plaintext = json.dumps(
        protected_record
    ).encode("utf-8")

    encrypted_data = cipher.encrypt(plaintext)

    ENCRYPTED_DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    ENCRYPTED_DATA_FILE.write_bytes(
        encrypted_data
    )

    write_log(
        f"BIOMETRIC_DATA_ENCRYPTED | "
        f"user_id={user_id}"
    )

    return {
        "status": "BIOMETRIC DATA PROTECTED",
        "encrypted_bytes": len(encrypted_data)
    }


def decrypt_biometric_data():
    if not ENCRYPTED_DATA_FILE.exists():
        return {
            "status": "NO BIOMETRIC DATA FOUND"
        }

    key = load_or_create_key()
    cipher = Fernet(key)

    encrypted_data = (
        ENCRYPTED_DATA_FILE.read_bytes()
    )

    decrypted_data = cipher.decrypt(
        encrypted_data
    )

    record = json.loads(
        decrypted_data.decode("utf-8")
    )

    write_log(
        f"BIOMETRIC_DATA_DECRYPTED | "
        f"user_id={record['user_id']}"
    )

    return {
        "status": "AUTHORIZED DECRYPTION SUCCESSFUL",
        "record": record
    }


if __name__ == "__main__":

    biometric_data = {
        "eye_tracking": {
            "gaze_x": 0.64,
            "gaze_y": 0.41,
            "pupil_diameter_mm": 3.8
        },
        "motion_tracking": {
            "head_x": 12.5,
            "head_y": 4.2,
            "head_z": -2.1,
            "movement_speed": 1.7
        }
    }

    print("=" * 60)
    print("GameShield AI - VR/AR Biometric Protection")
    print("=" * 60)

    protection = encrypt_biometric_data(
        "USER-DEMO-001",
        biometric_data
    )

    print("\nProtection Result")
    print("-" * 60)
    print(f"Status: {protection['status']}")
    print(
        f"Encrypted Data Size: "
        f"{protection['encrypted_bytes']} bytes"
    )

    verification = decrypt_biometric_data()

    print("\nAuthorized Verification")
    print("-" * 60)
    print(f"Status: {verification['status']}")

    if "record" in verification:
        print(
            "Protected User: "
            f"{verification['record']['user_id']}"
        )
        print(
            "Eye Tracking Protected: True"
        )
        print(
            "Motion Tracking Protected: True"
        )