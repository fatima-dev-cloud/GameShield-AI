from src.audio_transcription.vosk_transcriber import (
    transcribe_wav,
)
from src.content_moderation.moderator import (
    moderate_text,
)


class VoiceModerationError(Exception):
    """Raised when the voice moderation pipeline fails."""


def moderate_voice(audio_file, model_path) -> dict:
    """
    Transcribe a local WAV file and moderate its transcript.

    Existing transcription exceptions propagate unchanged.

    Args:
        audio_file:
            Path to the local WAV file.
        model_path:
            Path to the local Vosk model directory.

    Returns:
        A dictionary containing the transcript and moderation result.

    Raises:
        VoiceModerationError:
            If transcription returns a non-string value or text
            moderation fails.
    """
    transcript = transcribe_wav(
        audio_file,
        model_path,
    )

    if not isinstance(transcript, str):
        raise VoiceModerationError(
            "Audio transcription returned an invalid result"
        )

    try:
        moderation_result = moderate_text(
            transcript
        )
    except Exception as exc:
        raise VoiceModerationError(
            "Text moderation failed after audio transcription"
        ) from exc

    return {
        "transcription": transcript,
        "moderation": moderation_result,
    }