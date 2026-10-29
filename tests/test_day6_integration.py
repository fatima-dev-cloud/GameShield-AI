from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from app import VOICE_MAX_REQUEST_BYTES, app

from audio_transcription.vosk_transcriber import (
    AudioTranscriptionError,
    InvalidWavFormatError,
    MAX_AUDIO_SIZE_BYTES,
    SpeechModelNotFoundError,
)
from voice_moderation.voice_moderator import (
    VoiceModerationError,
)


@pytest.fixture
def client():
    previous_testing = app.config.get(
        "TESTING", False
    )
    previous_model_path = app.config.get(
        "VOSK_MODEL_PATH"
    )

    app.config.update(
        TESTING=True,
        VOSK_MODEL_PATH="/configured/vosk-model",
    )

    with app.test_client() as test_client:
        yield test_client

    app.config["TESTING"] = previous_testing
    app.config["VOSK_MODEL_PATH"] = (
        previous_model_path
    )

def _voice_upload(audio_data=b"RIFF-test-data"):
    return {
        "audio": (
            BytesIO(audio_data),
            "sample.wav",
        )
    }


def test_voice_api_connects_existing_pipeline(client):
    expected = {
        "transcription": "good game",
        "moderation": {
            "action": "ALLOW",
        },
    }

    with patch(
        "app.moderate_voice",
        return_value=expected,
    ) as moderate:
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data == {
        "platform": "GameShield AI",
        "module": "AI Voice Moderation",
        "analysis": expected,
    }

    assert moderate.call_count == 1

    audio_path, model_path = moderate.call_args.args

    assert audio_path.suffix == ".wav"
    assert not audio_path.exists()
    assert model_path == "/configured/vosk-model"


def test_voice_api_requires_server_model_configuration(
    client,
):
    app.config["VOSK_MODEL_PATH"] = None

    with patch("app.moderate_voice") as moderate:
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 503
    assert response.get_json() == {
        "error": (
            "Voice moderation model is not configured."
        )
    }
    moderate.assert_not_called()


def test_voice_api_does_not_accept_client_paths(client):
    with patch("app.moderate_voice") as moderate:
        response = client.post(
            "/api/moderation/voice",
            data={
                "audio_path": "/etc/passwd",
                "model_path": "/client/model",
            },
        )

    assert response.status_code == 400
    moderate.assert_not_called()


def test_voice_api_requires_audio_upload(client):
    response = client.post(
        "/api/moderation/voice"
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "A WAV file is required in the audio field."
        )
    }


def test_voice_api_rejects_oversized_audio(client):
    oversized_audio = (
        b"x" * (MAX_AUDIO_SIZE_BYTES + 1)
    )

    with patch("app.moderate_voice") as moderate:
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(oversized_audio),
            content_type="multipart/form-data",
        )

    assert response.status_code == 413
    moderate.assert_not_called()


def test_voice_api_sanitizes_invalid_wav_error(client):
    with patch(
        "app.moderate_voice",
        side_effect=InvalidWavFormatError(
            "private temporary path"
        ),
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(b"not-a-wav"),
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "Audio must be an uncompressed 16-bit "
            "mono PCM WAV file."
        )
    }
    assert "private temporary path" not in (
        response.get_data(as_text=True)
    )


def test_voice_api_maps_missing_model_without_path_leak(
    client,
):
    with patch(
        "app.moderate_voice",
        side_effect=SpeechModelNotFoundError(
            "/private/model/path"
        ),
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 503
    assert response.get_json() == {
        "error": "Voice moderation model is unavailable."
    }
    assert "/private/model/path" not in (
        response.get_data(as_text=True)
    )


def test_voice_api_maps_transcription_failure(client):
    with patch(
        "app.moderate_voice",
        side_effect=AudioTranscriptionError(
            "internal transcription details"
        ),
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 422
    assert response.get_json() == {
        "error": "Audio could not be transcribed."
    }
    assert "internal transcription details" not in (
        response.get_data(as_text=True)
    )


def test_voice_api_maps_moderation_failure(client):
    with patch(
        "app.moderate_voice",
        side_effect=VoiceModerationError(
            "internal moderation details"
        ),
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 500
    assert response.get_json() == {
        "error": (
            "Voice moderation could not be completed."
        )
    }
    assert "internal moderation details" not in (
        response.get_data(as_text=True)
    )


def test_voice_api_removes_temporary_file_on_failure(
    client,
):
    captured_path = None

    def fail_after_capture(audio_path, model_path):
        nonlocal captured_path
        captured_path = audio_path

        assert model_path == "/configured/vosk-model"
        assert audio_path.exists()

        raise InvalidWavFormatError("invalid WAV")

    with patch(
        "app.moderate_voice",
        side_effect=fail_after_capture,
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(b"not-a-wav"),
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert captured_path is not None
    assert not captured_path.exists()
    
def test_voice_api_removes_temporary_file_when_write_fails(
    client, tmp_path
):
    temporary_path = tmp_path / "partial-voice-upload.wav"
    temporary_path.write_bytes(b"partial")

    temporary_file = MagicMock()
    temporary_file.name = str(temporary_path)
    temporary_file.write.side_effect = OSError(
        "simulated write failure"
    )
    temporary_file.__enter__.return_value = temporary_file
    temporary_file.__exit__.return_value = False

    with (
        patch(
            "app.tempfile.NamedTemporaryFile",
            return_value=temporary_file,
        ),
        patch("app.moderate_voice") as moderate,
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(),
            content_type="multipart/form-data",
        )

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Voice moderation could not be completed."
    }
    assert not temporary_path.exists()
    moderate.assert_not_called()

    
def test_dashboard_exposes_voice_controls(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b'id="voiceAudioFile"' in response.data
    assert b'id="moderateVoiceButton"' in response.data
    assert b'id="voiceModerationResult"' in response.data


def test_dashboard_script_connects_voice_endpoint(client):
    response = client.get(
        "/static/dashboard.js"
    )

    assert response.status_code == 200
    assert b'"/api/moderation/voice"' in response.data
    assert b"new FormData()" in response.data
    assert b'formData.append(' in response.data
    
def test_voice_api_rejects_request_before_processing(client):
    oversized_request = b"x" * (VOICE_MAX_REQUEST_BYTES + 1)

    with (
        patch("app.moderate_voice") as moderate,
        patch("app.tempfile.NamedTemporaryFile") as temporary_file,
    ):
        response = client.post(
            "/api/moderation/voice",
            data=_voice_upload(oversized_request),
            content_type="multipart/form-data",
        )

    assert response.status_code == 413
    assert response.get_json() == {
        "error": (
            "Voice upload exceeds the maximum "
            "permitted request size."
        )
    }
    temporary_file.assert_not_called()
    moderate.assert_not_called()