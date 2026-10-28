from unittest.mock import patch

import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    "invalid_body",
    [
        [],
        ["message"],
        "good game everyone",
        123,
        True,
    ],
)
def test_text_moderation_rejects_non_object_json(
    client,
    invalid_body,
):
    with patch(
        "src.app.moderate_text"
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            json=invalid_body,
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Valid JSON request required."
    }
    mock_moderate_text.assert_not_called()


def test_text_moderation_rejects_malformed_json(client):
    with patch(
        "src.app.moderate_text"
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            data='{"message":',
            content_type="application/json",
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Valid JSON request required."
    }
    mock_moderate_text.assert_not_called()


def test_text_moderation_rejects_missing_message(client):
    with patch(
        "src.app.moderate_text"
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            json={},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "message is required."
    }
    mock_moderate_text.assert_not_called()


@pytest.mark.parametrize(
    "invalid_message",
    [
        None,
        123,
        3.14,
        True,
        [],
        {},
    ],
)
def test_text_moderation_rejects_non_string_message(
    client,
    invalid_message,
):
    with patch(
        "src.app.moderate_text"
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            json={
                "message": invalid_message
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "message must be a string."
    }
    mock_moderate_text.assert_not_called()


def test_text_moderation_preserves_empty_message_handling(
    client,
):
    moderation_result = {
        "status": "REJECTED",
        "action": "BLOCK",
        "reason": "Empty message",
        "toxicity_probability": 0.0,
    }

    with patch(
        "src.app.moderate_text",
        return_value=moderation_result,
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            json={
                "message": ""
            },
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "platform": "GameShield AI",
        "module": "AI Content Moderation",
        "analysis": moderation_result,
    }
    mock_moderate_text.assert_called_once_with("")


def test_text_moderation_preserves_successful_response(
    client,
):
    moderation_result = {
        "status": "CONTENT SAFE",
        "action": "ALLOW",
        "risk_level": "LOW",
        "toxicity_probability": 10.0,
    }

    with patch(
        "src.app.moderate_text",
        return_value=moderation_result,
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            json={
                "message": "good game everyone"
            },
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "platform": "GameShield AI",
        "module": "AI Content Moderation",
        "analysis": moderation_result,
    }
    mock_moderate_text.assert_called_once_with(
        "good game everyone"
    )


def test_text_moderation_preserves_toxic_response(
    client,
):
    moderation_result = {
        "status": "TOXIC CONTENT DETECTED",
        "action": "BLOCK",
        "risk_level": "HIGH",
        "toxicity_probability": 80.0,
    }

    with patch(
        "src.app.moderate_text",
        return_value=moderation_result,
    ) as mock_moderate_text:
        response = client.post(
            "/api/moderation/text",
            json={
                "message": "shut up idiot"
            },
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "platform": "GameShield AI",
        "module": "AI Content Moderation",
        "analysis": moderation_result,
    }
    mock_moderate_text.assert_called_once_with(
        "shut up idiot"
    )