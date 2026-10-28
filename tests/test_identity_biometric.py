from base64 import urlsafe_b64decode, urlsafe_b64encode
from pathlib import Path

import pytest
from cryptography.fernet import InvalidToken

from identity_security import authentication
from identity_security import biometric_protection


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    paths = {
        "users": tmp_path / "data" / "users.json",
        "identity_log": tmp_path / "logs" / "identity.log",
        "biometric_key": tmp_path / "config" / "biometric.key",
        "biometric_data": tmp_path / "data" / "biometric.dat",
        "biometric_log": tmp_path / "logs" / "biometric.log",
    }

    for path in paths.values():
        assert isinstance(path, Path)
        path.resolve().relative_to(tmp_path.resolve())

    monkeypatch.setattr(authentication, "USER_FILE", paths["users"])
    monkeypatch.setattr(
        authentication,
        "LOG_FILE",
        paths["identity_log"],
    )
    monkeypatch.setattr(
        biometric_protection,
        "KEY_FILE",
        paths["biometric_key"],
    )
    monkeypatch.setattr(
        biometric_protection,
        "ENCRYPTED_DATA_FILE",
        paths["biometric_data"],
    )
    monkeypatch.setattr(
        biometric_protection,
        "LOG_FILE",
        paths["biometric_log"],
    )

    return paths


def register_synthetic_user():
    return authentication.register_user(
        "synthetic_player",
        "SyntheticPassword@2026",
        "SyntheticAvatar",
    )


def test_successful_user_registration(isolated_storage):
    result = register_synthetic_user()

    assert result["status"] == "REGISTRATION SUCCESSFUL"
    assert result["username"] == "synthetic_player"
    assert result["avatar_name"] == "SyntheticAvatar"
    assert isolated_storage["users"].exists()


def test_successful_login(isolated_storage):
    registration = register_synthetic_user()
    result = authentication.authenticate_user(
        "synthetic_player",
        "SyntheticPassword@2026",
    )

    assert registration["status"] == "REGISTRATION SUCCESSFUL"
    assert result["status"] == "AUTHENTICATION SUCCESSFUL"
    assert result["authenticated"] is True
    assert result["user_id"] == registration["user_id"]
    assert isinstance(result["session_token"], str)
    assert result["session_token"]


def test_incorrect_password_rejected(isolated_storage):
    register_synthetic_user()
    result = authentication.authenticate_user(
        "synthetic_player",
        "IncorrectPassword@2026",
    )

    assert result == {
        "status": "AUTHENTICATION FAILED",
        "authenticated": False,
        "message": "Invalid credentials.",
    }


def test_duplicate_user_registration_rejected(isolated_storage):
    first = register_synthetic_user()
    duplicate = register_synthetic_user()

    assert first["status"] == "REGISTRATION SUCCESSFUL"
    assert duplicate == {
        "status": "REGISTRATION FAILED",
        "message": "Username already exists.",
    }


@pytest.mark.parametrize(
    "malformed_user",
    [
        None,
        {},
        {"username": []},
        {
            "username": "synthetic_player",
            "user_id": "USER-SYNTHETIC",
        },
        {
            "username": "synthetic_player",
            "user_id": "USER-SYNTHETIC",
            "avatar_name": "SyntheticAvatar",
            "password_salt": "not-hex",
            "password_hash": "not-a-valid-hash",
        },
    ],
)
def test_malformed_user_records_fail_safely(
    isolated_storage,
    malformed_user,
):
    authentication.save_users({"users": [malformed_user]})
    original_database = isolated_storage["users"].read_bytes()

    registration = register_synthetic_user()
    login = authentication.authenticate_user(
        "synthetic_player",
        "SyntheticPassword@2026",
    )

    assert registration["status"] == "REGISTRATION FAILED"
    assert isolated_storage["users"].read_bytes() == original_database
    assert login == {
        "status": "AUTHENTICATION FAILED",
        "authenticated": False,
        "message": "Invalid credentials.",
    }


def test_synthetic_biometric_encryption_round_trip(
    isolated_storage,
):
    synthetic_data = {
        "eye_tracking": {"gaze_x": 0.25, "gaze_y": 0.75},
        "motion_tracking": {"movement_speed": 1.25},
    }

    protected = biometric_protection.encrypt_biometric_data(
        "USER-SYNTHETIC",
        synthetic_data,
    )
    decrypted = biometric_protection.decrypt_biometric_data()

    assert protected["status"] == "BIOMETRIC DATA PROTECTED"
    assert decrypted["status"] == (
        "AUTHORIZED DECRYPTION SUCCESSFUL"
    )
    assert decrypted["record"]["user_id"] == "USER-SYNTHETIC"
    assert decrypted["record"]["biometric_data"] == synthetic_data


def test_biometric_ciphertext_tampering_detected(
    isolated_storage,
):
    biometric_protection.encrypt_biometric_data(
        "USER-SYNTHETIC",
        {"eye_tracking": {"gaze_x": 0.5}},
    )
    token = isolated_storage["biometric_data"].read_bytes()
    decoded_token = bytearray(urlsafe_b64decode(token))
    ciphertext_start = 25
    ciphertext_end = len(decoded_token) - 32
    ciphertext_middle = (
        ciphertext_start + ciphertext_end
    ) // 2
    decoded_token[ciphertext_middle] ^= 1
    tampered_token = urlsafe_b64encode(decoded_token)
    isolated_storage["biometric_data"].write_bytes(
        tampered_token
    )

    with pytest.raises(InvalidToken):
        biometric_protection.decrypt_biometric_data()
