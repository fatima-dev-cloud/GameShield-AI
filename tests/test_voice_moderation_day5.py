from pathlib import Path
from unittest.mock import patch

import pytest

from src.audio_transcription.vosk_transcriber import (
    AudioFileTooLargeError,
    InvalidWavFormatError,
    SpeechModelNotFoundError,
    TranscriptionError,
)
from src.voice_moderation import voice_moderator


SAFE_MODERATION_RESULT = {
    "status": "CONTENT SAFE",
    "action": "ALLOW",
    "risk_level": "LOW",
    "toxicity_probability": 10.0,
}

TOXIC_MODERATION_RESULT = {
    "status": "TOXIC CONTENT DETECTED",
    "action": "BLOCK",
    "risk_level": "HIGH",
    "toxicity_probability": 80.0,
}

EMPTY_MODERATION_RESULT = {
    "status": "REJECTED",
    "action": "BLOCK",
    "reason": "Empty message",
    "toxicity_probability": 0.0,
}


def test_safe_transcription_returns_structured_result():
    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="good game everyone",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=SAFE_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        result = voice_moderator.moderate_voice(
            "safe.wav",
            "vosk-model",
        )

    assert result == {
        "transcription": "good game everyone",
        "moderation": SAFE_MODERATION_RESULT,
    }
    mock_transcribe.assert_called_once_with(
        "safe.wav",
        "vosk-model",
    )
    mock_moderate.assert_called_once_with(
        "good game everyone"
    )


def test_toxic_transcription_returns_structured_result():
    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="shut up idiot",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=TOXIC_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        result = voice_moderator.moderate_voice(
            "toxic.wav",
            "vosk-model",
        )

    assert result == {
        "transcription": "shut up idiot",
        "moderation": TOXIC_MODERATION_RESULT,
    }
    mock_transcribe.assert_called_once_with(
        "toxic.wav",
        "vosk-model",
    )
    mock_moderate.assert_called_once_with(
        "shut up idiot"
    )


def test_empty_transcription_is_passed_to_moderation():
    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=EMPTY_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        result = voice_moderator.moderate_voice(
            "silent.wav",
            "vosk-model",
        )

    assert result == {
        "transcription": "",
        "moderation": EMPTY_MODERATION_RESULT,
    }
    mock_transcribe.assert_called_once_with(
        "silent.wav",
        "vosk-model",
    )
    mock_moderate.assert_called_once_with("")


def test_path_objects_are_forwarded_unchanged():
    audio_path = Path(
        "/tmp/gameshield-audio-test/test_voice.wav"
    )
    model_path = Path(
        "models/vosk/vosk-model-small-en-us-0.15"
    )

    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="good game",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=SAFE_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        voice_moderator.moderate_voice(
            audio_path,
            model_path,
        )

    mock_transcribe.assert_called_once_with(
        audio_path,
        model_path,
    )
    mock_moderate.assert_called_once_with(
        "good game"
    )


def test_string_paths_are_forwarded_unchanged():
    audio_path = "/tmp/test_voice.wav"
    model_path = (
        "models/vosk/"
        "vosk-model-small-en-us-0.15"
    )

    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="well played",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=SAFE_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        voice_moderator.moderate_voice(
            audio_path,
            model_path,
        )

    mock_transcribe.assert_called_once_with(
        audio_path,
        model_path,
    )
    mock_moderate.assert_called_once_with(
        "well played"
    )


def test_transcription_whitespace_is_preserved():
    transcript = "  good game everyone  \n"

    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value=transcript,
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=SAFE_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        result = voice_moderator.moderate_voice(
            "voice.wav",
            "vosk-model",
        )

    assert result["transcription"] == transcript
    mock_transcribe.assert_called_once_with(
        "voice.wav",
        "vosk-model",
    )
    mock_moderate.assert_called_once_with(
        transcript
    )


@pytest.mark.parametrize(
    "transcription_error",
    [
        FileNotFoundError("Audio file not found"),
        AudioFileTooLargeError(
            "Audio file exceeds maximum size"
        ),
        InvalidWavFormatError(
            "Invalid WAV format"
        ),
        SpeechModelNotFoundError(
            "Speech model not found"
        ),
        TranscriptionError(
            "Transcription failed"
        ),
        TypeError(
            "audio_file must be path-like"
        ),
    ],
    ids=[
        "missing-audio",
        "oversized-audio",
        "invalid-wav",
        "missing-model",
        "vosk-failure",
        "invalid-path-type",
    ],
)
def test_transcription_errors_propagate_unchanged(
    transcription_error,
):
    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            side_effect=transcription_error,
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
        ) as mock_moderate,
    ):
        with pytest.raises(
            type(transcription_error)
        ) as raised:
            voice_moderator.moderate_voice(
                "voice.wav",
                "vosk-model",
            )

    assert raised.value is transcription_error
    mock_transcribe.assert_called_once_with(
        "voice.wav",
        "vosk-model",
    )
    mock_moderate.assert_not_called()


@pytest.mark.parametrize(
    "invalid_transcription",
    [
        None,
        123,
        3.14,
        True,
        [],
        {},
        b"spoken words",
    ],
)
def test_non_string_transcription_is_rejected(
    invalid_transcription,
):
    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value=invalid_transcription,
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
        ) as mock_moderate,
    ):
        with pytest.raises(
            voice_moderator.VoiceModerationError,
            match=(
                "^Audio transcription returned "
                "an invalid result$"
            ),
        ) as raised:
            voice_moderator.moderate_voice(
                "voice.wav",
                "vosk-model",
            )

    assert raised.value.__cause__ is None
    assert "voice.wav" not in str(raised.value)
    assert str(invalid_transcription) not in str(
        raised.value
    )

    mock_transcribe.assert_called_once_with(
        "voice.wav",
        "vosk-model",
    )
    mock_moderate.assert_not_called()


def test_moderation_failure_is_wrapped_and_chained():
    moderation_error = RuntimeError(
        "moderation model failure"
    )

    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="private spoken content",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            side_effect=moderation_error,
        ) as mock_moderate,
    ):
        with pytest.raises(
            voice_moderator.VoiceModerationError,
            match=(
                "^Text moderation failed after "
                "audio transcription$"
            ),
        ) as raised:
            voice_moderator.moderate_voice(
                "/private/path/voice.wav",
                "private-model-path",
            )

    assert raised.value.__cause__ is moderation_error

    public_error = str(raised.value)
    assert "/private/path/voice.wav" not in public_error
    assert "private-model-path" not in public_error
    assert "private spoken content" not in public_error
    assert "moderation model failure" not in public_error

    mock_transcribe.assert_called_once_with(
        "/private/path/voice.wav",
        "private-model-path",
    )
    mock_moderate.assert_called_once_with(
        "private spoken content"
    )


def test_pipeline_calls_each_dependency_exactly_once():
    with (
        patch.object(
            voice_moderator,
            "transcribe_wav",
            return_value="good game everyone",
        ) as mock_transcribe,
        patch.object(
            voice_moderator,
            "moderate_text",
            return_value=SAFE_MODERATION_RESULT,
        ) as mock_moderate,
    ):
        result = voice_moderator.moderate_voice(
            "voice.wav",
            "vosk-model",
        )

    assert result == {
        "transcription": "good game everyone",
        "moderation": SAFE_MODERATION_RESULT,
    }
    assert mock_transcribe.call_count == 1
    assert mock_moderate.call_count == 1