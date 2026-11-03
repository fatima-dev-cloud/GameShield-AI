import json
import os
import wave
from pathlib import Path

from vosk import KaldiRecognizer, Model


MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024
AUDIO_CHUNK_FRAMES = 4000


class AudioTranscriptionError(Exception):
    """Base exception for audio transcription failures."""


class AudioFileTooLargeError(AudioTranscriptionError):
    """Raised when an audio file exceeds the permitted size."""


class InvalidWavFormatError(AudioTranscriptionError):
    """Raised when an audio file is not a supported WAV file."""


class SpeechModelNotFoundError(AudioTranscriptionError):
    """Raised when the configured Vosk model directory is missing."""


class TranscriptionError(AudioTranscriptionError):
    """Raised when Vosk cannot transcribe valid audio."""


def _resolve_path(value, argument_name):
    if not isinstance(value, (str, os.PathLike)):
        raise TypeError(
            f"{argument_name} must be a string or path-like object"
        )

    try:
        return Path(value).expanduser()
    except (TypeError, ValueError, OSError) as exc:
        raise TypeError(
            f"{argument_name} must be a valid filesystem path"
        ) from exc


def _validate_audio_file(audio_path):
    if not audio_path.is_file():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    try:
        file_size = audio_path.stat().st_size
    except OSError as exc:
        raise AudioTranscriptionError(
            f"Unable to inspect audio file: {audio_path}"
        ) from exc

    if file_size > MAX_AUDIO_SIZE_BYTES:
        raise AudioFileTooLargeError(
            "Audio file exceeds the maximum permitted size "
            "of 10 MB"
        )


def _validate_model_path(model_path):
    if not model_path.is_dir():
        raise SpeechModelNotFoundError(
            f"Vosk speech model not found: {model_path}"
        )


def _validate_wav_format(wav_file):
    if wav_file.getnchannels() != 1:
        raise InvalidWavFormatError(
            "WAV audio must contain exactly one channel"
        )

    if wav_file.getsampwidth() != 2:
        raise InvalidWavFormatError(
            "WAV audio must use 16-bit samples"
        )

    if wav_file.getcomptype() != "NONE":
        raise InvalidWavFormatError(
            "WAV audio must use uncompressed PCM encoding"
        )

    if wav_file.getframerate() <= 0:
        raise InvalidWavFormatError(
            "WAV audio must have a positive sample rate"
        )


def _extract_text(raw_result):
    try:
        result = json.loads(raw_result)
    except (TypeError, json.JSONDecodeError) as exc:
        raise TranscriptionError(
            "Vosk returned malformed transcription JSON"
        ) from exc

    if not isinstance(result, dict):
        raise TranscriptionError(
            "Vosk returned an invalid transcription result"
        )

    text = result.get("text", "")

    if not isinstance(text, str):
        raise TranscriptionError(
            "Vosk returned an invalid transcription result"
        )

    return text.strip()


def transcribe_wav(audio_file, model_path) -> str:
    """
    Transcribe a local 16-bit mono PCM WAV file using Vosk.

    Args:
        audio_file:
            Path to a local WAV file no larger than 10 MB.
        model_path:
            Path to an extracted local Vosk speech model.

    Returns:
        Recognized text, or an empty string when no speech is detected.

    Raises:
        TypeError:
            If either path argument is not a string or path-like object.
        FileNotFoundError:
            If the audio file does not exist.
        AudioFileTooLargeError:
            If the audio file exceeds 10 MB.
        InvalidWavFormatError:
            If the file is not a valid 16-bit mono PCM WAV file.
        SpeechModelNotFoundError:
            If the Vosk model directory does not exist.
        TranscriptionError:
            If model initialization, recognition, or result parsing fails.
    """
    audio_path = _resolve_path(
        audio_file,
        "audio_file",
    )
    speech_model_path = _resolve_path(
        model_path,
        "model_path",
    )

    _validate_audio_file(audio_path)
    _validate_model_path(speech_model_path)

    try:
        wav_context = wave.open(
            str(audio_path),
            "rb",
        )
    except (wave.Error, EOFError) as exc:
        raise InvalidWavFormatError(
            "Audio file is not a valid WAV file"
        ) from exc
    except OSError as exc:
        raise AudioTranscriptionError(
            f"Unable to open audio file: {audio_path}"
        ) from exc

    with wav_context as wav_file:
        _validate_wav_format(wav_file)

        sample_rate = wav_file.getframerate()

        try:
            model = Model(
                str(speech_model_path)
            )

            recognizer = KaldiRecognizer(
                model,
                sample_rate,
            )
        except Exception as exc:
            raise TranscriptionError(
                "Unable to initialize Vosk transcription"
            ) from exc

        text_segments = []

        try:
            while True:
                audio_data = wav_file.readframes(
                    AUDIO_CHUNK_FRAMES
                )

                if not audio_data:
                    break

                if recognizer.AcceptWaveform(
                    audio_data
                ):
                    segment = _extract_text(
                        recognizer.Result()
                    )

                    if segment:
                        text_segments.append(
                            segment
                        )

            final_segment = _extract_text(
                recognizer.FinalResult()
            )

            if final_segment:
                text_segments.append(
                    final_segment
                )
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError(
                "Vosk transcription failed"
            ) from exc

    return " ".join(text_segments)