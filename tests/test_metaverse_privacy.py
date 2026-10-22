
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app import app


def test_privacy_rejects_string_false():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/api/identity/privacy",
        json={
            "user_id": "USER-PRIVACY-TEST",
            "data_type": "eye_tracking",
            "allowed": "false"
        }
    )

    assert response.status_code == 400
    assert "allowed must be" in response.get_json()["error"]


def test_privacy_rejects_numeric_permission():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/api/identity/privacy",
        json={
            "user_id": "USER-PRIVACY-TEST",
            "data_type": "motion_tracking",
            "allowed": 1
        }
    )

    assert response.status_code == 400


def test_privacy_rejects_missing_permission():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/api/identity/privacy",
        json={
            "user_id": "USER-PRIVACY-TEST",
            "data_type": "spatial_audio"
        }
    )

    assert response.status_code == 400


def test_biometric_rejects_missing_consent(monkeypatch):
    from identity_security import privacy_controls

    def deny_access(user_id, data_type):
        return {
            "user_id": user_id,
            "data_type": data_type,
            "access": "DENIED"
        }

    monkeypatch.setattr(
        "app.check_data_access",
        deny_access
    )

    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/api/identity/biometric/protect",
        json={
            "user_id": "USER-TEST-DENIED",
            "biometric_data": {
                "eye_tracking": {"x": 0.45},
                "motion_pattern": [0.12, 0.34]
            }
        }
    )

    assert response.status_code == 403
    assert response.get_json()["denied_permissions"] == [
        "eye_tracking",
        "motion_tracking"
    ]


def test_biometric_accepts_allowed_consent(monkeypatch):
    def allow_access(user_id, data_type):
        return {
            "user_id": user_id,
            "data_type": data_type,
            "access": "ALLOWED"
        }

    def fake_encrypt(user_id, biometric_data):
        return {
            "status": "BIOMETRIC DATA PROTECTED",
            "encrypted_bytes": 100
        }

    monkeypatch.setattr(
        "app.check_data_access",
        allow_access
    )

    monkeypatch.setattr(
        "app.encrypt_biometric_data",
        fake_encrypt
    )

    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/api/identity/biometric/protect",
        json={
            "user_id": "USER-TEST-ALLOWED",
            "biometric_data": {
                "eye_tracking": {"x": 0.45},
                "motion_pattern": [0.12, 0.34]
            }
        }
    )

    assert response.status_code == 200
    assert response.get_json()["result"]["status"] == (
        "BIOMETRIC DATA PROTECTED"
    )
