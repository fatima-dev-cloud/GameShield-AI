import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app
from infrastructure_security.rate_limiter import (
    request_history,
    blocked_clients,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True

    request_history.clear()
    blocked_clients.clear()

    with app.test_client() as test_client:
        yield test_client

    request_history.clear()
    blocked_clients.clear()


def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"GameShield AI" in response.data


def test_status_api(client):
    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "online"


def test_anticheat_rejects_missing_data(client):
    response = client.post(
        "/api/anti-cheat/analyze",
        json={},
    )

    assert response.status_code == 400


def test_registration_rejects_missing_data(client):
    response = client.post(
        "/api/identity/register",
        json={},
    )

    assert response.status_code == 400


def test_moderation_rejects_missing_message(client):
    response = client.post(
        "/api/moderation/text",
        json={},
    )

    assert response.status_code == 400


def test_rate_limiter_blocks_excessive_requests(client):
    responses = []

    for _ in range(12):
        response = client.get("/api/status")
        responses.append(response.status_code)

    assert 429 in responses