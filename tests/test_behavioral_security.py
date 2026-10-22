
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app
from anti_cheat.behavioral_security import (
    detect_account_sharing,
    detect_rank_boosting,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_account_sharing_suspicious():
    result = detect_account_sharing({
        "distance_km": 5000,
        "time_difference_minutes": 20,
        "device_changed": True,
        "behavior_change_score": 0.90,
    })

    assert result["risk_level"] == "HIGH"
    assert result["suspicious"] is True
    assert result["risk_score"] == 100


def test_account_sharing_legitimate():
    result = detect_account_sharing({
        "distance_km": 10,
        "time_difference_minutes": 120,
        "device_changed": False,
        "behavior_change_score": 0.10,
    })

    assert result["risk_level"] == "LOW"
    assert result["suspicious"] is False


def test_rank_boosting_suspicious():
    result = detect_rank_boosting({
        "previous_win_rate": 0.35,
        "current_win_rate": 0.90,
        "rank_increase": 7,
        "matches_played": 8,
        "performance_change_score": 0.85,
    })

    assert result["risk_level"] == "HIGH"
    assert result["suspicious"] is True


def test_rank_boosting_legitimate():
    result = detect_rank_boosting({
        "previous_win_rate": 0.45,
        "current_win_rate": 0.50,
        "rank_increase": 1,
        "matches_played": 25,
        "performance_change_score": 0.10,
    })

    assert result["risk_level"] == "LOW"
    assert result["suspicious"] is False


def test_account_sharing_api(client):
    response = client.post(
        "/api/anti-cheat/account-sharing",
        json={
            "distance_km": 5000,
            "time_difference_minutes": 20,
            "device_changed": True,
            "behavior_change_score": 0.90,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["risk_level"] == "HIGH"


def test_rank_boosting_api(client):
    response = client.post(
        "/api/anti-cheat/rank-boosting",
        json={
            "previous_win_rate": 0.35,
            "current_win_rate": 0.90,
            "rank_increase": 7,
            "matches_played": 8,
            "performance_change_score": 0.85,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["risk_level"] == "HIGH"


def test_account_sharing_invalid_input(client):
    response = client.post(
        "/api/anti-cheat/account-sharing",
        json={
            "distance_km": -10,
            "time_difference_minutes": 20,
            "device_changed": True,
            "behavior_change_score": 0.90,
        },
    )

    assert response.status_code == 400


def test_rank_boosting_invalid_input(client):
    response = client.post(
        "/api/anti-cheat/rank-boosting",
        json={
            "previous_win_rate": 1.5,
            "current_win_rate": 0.90,
            "rank_increase": 7,
            "matches_played": 8,
            "performance_change_score": 0.85,
        },
    )

    assert response.status_code == 400