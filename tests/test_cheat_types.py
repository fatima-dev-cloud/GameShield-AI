
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app
from anti_cheat.cheat_type_detector import analyze_cheat_types


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


LEGITIMATE = {
    "accuracy": 0.48,
    "headshot_rate": 0.22,
    "reaction_time": 280,
    "impossible_actions": 0,
    "hidden_enemy_tracking_events": 0,
    "repetitive_input_score": 0.20,
}

AIMBOT = {
    **LEGITIMATE,
    "accuracy": 0.98,
    "headshot_rate": 0.96,
    "reaction_time": 40,
}

WALLHACK = {
    **LEGITIMATE,
    "hidden_enemy_tracking_events": 9,
}

AUTOMATION = {
    **LEGITIMATE,
    "impossible_actions": 12,
    "repetitive_input_score": 0.98,
}


def test_legitimate_player():
    result = analyze_cheat_types(LEGITIMATE)

    assert result["risk_level"] == "LOW"
    assert result["suspicious"] is False
    assert result["detected_categories"] == []


def test_aimbot_detection():
    result = analyze_cheat_types(AIMBOT)

    assert "AIMBOT" in result["detected_categories"]


def test_wallhack_detection():
    result = analyze_cheat_types(WALLHACK)

    assert "WALLHACK" in result["detected_categories"]


def test_automated_cheating_detection():
    result = analyze_cheat_types(AUTOMATION)

    assert "AUTOMATED_CHEATING" in result["detected_categories"]


@pytest.mark.parametrize(
    "payload, expected_category",
    [
        (AIMBOT, "AIMBOT"),
        (WALLHACK, "WALLHACK"),
        (AUTOMATION, "AUTOMATED_CHEATING"),
    ],
)
def test_cheat_type_api(client, payload, expected_category):
    response = client.post(
        "/api/anti-cheat/cheat-types",
        json=payload,
    )

    assert response.status_code == 200
    assert expected_category in (
        response.get_json()["detected_categories"]
    )


def test_legitimate_player_api(client):
    response = client.post(
        "/api/anti-cheat/cheat-types",
        json=LEGITIMATE,
    )

    assert response.status_code == 200
    assert response.get_json()["suspicious"] is False


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"accuracy": 0.5},
        {**LEGITIMATE, "accuracy": 1.5},
        {**LEGITIMATE, "reaction_time": -10},
        {**LEGITIMATE, "impossible_actions": -1},
        {**LEGITIMATE, "repetitive_input_score": 2},
        {**LEGITIMATE, "hidden_enemy_tracking_events": 2.5},
        {**LEGITIMATE, "accuracy": True},
    ],
)
def test_invalid_cheat_type_input(client, invalid_payload):
    response = client.post(
        "/api/anti-cheat/cheat-types",
        json=invalid_payload,
    )

    assert response.status_code == 400


def test_non_json_input(client):
    response = client.post(
        "/api/anti-cheat/cheat-types",
        data="invalid input",
        content_type="text/plain",
    )

    assert response.status_code == 400