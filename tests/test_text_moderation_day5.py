from unittest.mock import MagicMock, patch

import pytest

from src.content_moderation import moderator


@pytest.mark.parametrize(
    "empty_text",
    [
        "",
        "   ",
        "\t\n",
    ],
)
def test_empty_text_is_rejected_before_model_loading(
    empty_text
):
    with (
        patch.object(
            moderator,
            "load_model"
        ) as mock_load_model,
        patch.object(
            moderator,
            "write_moderation_log"
        ) as mock_write_log,
    ):
        result = moderator.moderate_text(
            empty_text
        )

    assert result == {
        "status": "REJECTED",
        "action": "BLOCK",
        "reason": "Empty message",
        "toxicity_probability": 0.0,
    }
    mock_load_model.assert_not_called()
    mock_write_log.assert_not_called()


@pytest.mark.parametrize(
    "invalid_text",
    [
        None,
        123,
        3.14,
        True,
        ["good game everyone"],
        {"text": "good game everyone"},
    ],
)
def test_non_string_input_raises_type_error_before_model_loading(
    invalid_text
):
    with (
        patch.object(
            moderator,
            "load_model"
        ) as mock_load_model,
        patch.object(
            moderator,
            "write_moderation_log"
        ) as mock_write_log,
    ):
        with pytest.raises(
            TypeError,
            match=r"^text must be a string$",
        ):
            moderator.moderate_text(
                invalid_text
            )

    mock_load_model.assert_not_called()
    mock_write_log.assert_not_called()


def test_safe_text_preserves_response_and_logging_behavior():
    model = MagicMock()
    model.predict.return_value = [0]
    model.predict_proba.return_value = [
        [0.9, 0.1]
    ]
    model.classes_ = [0, 1]

    with (
        patch.object(
            moderator,
            "load_model",
            return_value=model,
        ) as mock_load_model,
        patch.object(
            moderator,
            "write_moderation_log",
        ) as mock_write_log,
    ):
        result = moderator.moderate_text(
            "  good game everyone  "
        )

    assert result == {
        "status": "CONTENT SAFE",
        "action": "ALLOW",
        "risk_level": "LOW",
        "toxicity_probability": 10.0,
    }

    mock_load_model.assert_called_once_with()
    model.predict.assert_called_once_with(
        ["good game everyone"]
    )
    model.predict_proba.assert_called_once_with(
        ["good game everyone"]
    )
    mock_write_log.assert_called_once_with(
        "TEXT_MODERATION | "
        "status=CONTENT SAFE | "
        "action=ALLOW | "
        "risk=LOW | "
        "toxicity=10.0%"
    )


def test_toxic_text_preserves_response_and_logging_behavior():
    model = MagicMock()
    model.predict.return_value = [1]
    model.predict_proba.return_value = [
        [0.2, 0.8]
    ]
    model.classes_ = [0, 1]

    with (
        patch.object(
            moderator,
            "load_model",
            return_value=model,
        ) as mock_load_model,
        patch.object(
            moderator,
            "write_moderation_log",
        ) as mock_write_log,
    ):
        result = moderator.moderate_text(
            "shut up idiot"
        )

    assert result == {
        "status": "TOXIC CONTENT DETECTED",
        "action": "BLOCK",
        "risk_level": "HIGH",
        "toxicity_probability": 80.0,
    }

    mock_load_model.assert_called_once_with()
    model.predict.assert_called_once_with(
        ["shut up idiot"]
    )
    model.predict_proba.assert_called_once_with(
        ["shut up idiot"]
    )
    mock_write_log.assert_called_once_with(
        "TEXT_MODERATION | "
        "status=TOXIC CONTENT DETECTED | "
        "action=BLOCK | "
        "risk=HIGH | "
        "toxicity=80.0%"
    )