import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

USER_FILE = BASE_DIR / "data" / "users.json"
LOG_FILE = BASE_DIR / "logs" / "identity_security.log"

PBKDF2_ITERATIONS = 200_000


def load_users():
    if not USER_FILE.exists():
        return {"users": []}

    with open(USER_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(database):
    USER_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(database, file, indent=4)


def write_identity_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )

    return salt.hex(), password_hash.hex()


def verify_password(password, salt_hex, stored_hash):
    salt = bytes.fromhex(salt_hex)

    _, calculated_hash = hash_password(
        password,
        salt
    )

    return hmac.compare_digest(
        calculated_hash,
        stored_hash
    )


def register_user(username, password, avatar_name):
    database = load_users()

    username = username.strip()

    if not username:
        return {
            "status": "REGISTRATION FAILED",
            "message": "Username cannot be empty."
        }

    if len(password) < 8:
        return {
            "status": "REGISTRATION FAILED",
            "message": "Password must contain at least 8 characters."
        }

    for user in database["users"]:
        if user["username"].lower() == username.lower():
            return {
                "status": "REGISTRATION FAILED",
                "message": "Username already exists."
            }

    salt, password_hash = hash_password(password)

    user = {
        "user_id": "USER-" + secrets.token_hex(5).upper(),
        "username": username,
        "avatar_name": avatar_name,
        "password_salt": salt,
        "password_hash": password_hash,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds")
    }

    database["users"].append(user)
    save_users(database)

    write_identity_log(
        f"USER_REGISTERED | "
        f"user_id={user['user_id']} | "
        f"username={username}"
    )

    return {
        "status": "REGISTRATION SUCCESSFUL",
        "user_id": user["user_id"],
        "username": username,
        "avatar_name": avatar_name
    }


def authenticate_user(username, password):
    database = load_users()

    for user in database["users"]:

        if user["username"].lower() == username.lower():

            password_valid = verify_password(
                password,
                user["password_salt"],
                user["password_hash"]
            )

            if password_valid:
                session_token = secrets.token_urlsafe(32)

                write_identity_log(
                    f"LOGIN_SUCCESS | "
                    f"user_id={user['user_id']} | "
                    f"username={username}"
                )

                return {
                    "status": "AUTHENTICATION SUCCESSFUL",
                    "authenticated": True,
                    "user_id": user["user_id"],
                    "avatar_name": user["avatar_name"],
                    "session_token": session_token
                }

            write_identity_log(
                f"LOGIN_FAILED | username={username}"
            )

            return {
                "status": "AUTHENTICATION FAILED",
                "authenticated": False,
                "message": "Invalid credentials."
            }

    write_identity_log(
        f"LOGIN_FAILED | username={username}"
    )

    return {
        "status": "AUTHENTICATION FAILED",
        "authenticated": False,
        "message": "Invalid credentials."
    }


if __name__ == "__main__":

    print("=" * 60)
    print("GameShield AI - Metaverse Identity Security")
    print("=" * 60)

    registration = register_user(
        username="vr_player_01",
        password="GameShield@2026",
        avatar_name="CyberGuardian"
    )

    print("\nRegistration")
    print("-" * 60)
    print(f"Status: {registration['status']}")

    if "user_id" in registration:
        print(f"User ID: {registration['user_id']}")

    login = authenticate_user(
        username="vr_player_01",
        password="GameShield@2026"
    )

    print("\nSecure Authentication")
    print("-" * 60)
    print(f"Status: {login['status']}")
    print(
        f"Authenticated: "
        f"{login.get('authenticated', False)}"
    )

    if login.get("authenticated"):
        print(f"User ID: {login['user_id']}")
        print(f"Avatar: {login['avatar_name']}")
        print(
            "Secure Session Token Generated: "
            f"{login['session_token'][:12]}..."
        )