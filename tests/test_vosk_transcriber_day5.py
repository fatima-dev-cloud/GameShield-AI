import importlib
import json
from unittest.mock import MagicMock, call, patch

import pytest
import vosk

from src.audio_transcription import vosk_transcriber


def create_audio_file(tmp_path, content=b"audio"):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(content)
    return audio_path


def create_model_directory(tmp_path):
    model_path = tmp_path / "vosk-model"
    model_path.mkdir()
    return model_path


def create_wav_context(
    *,
    channels=1,
    sample_width=2,
    compression_type="NONE",
    sample_rate=16000,
    audio_chunks=None,
):
    if audio_chunks is None:
        audio_chunks = [b"audio-data", b""]

    wav_file = MagicMock()
    wav_file.getnchannels.return_value = channels
    wav_file.getsampwidth.return_value = sample_width
    wav_file.getcomptype.return_value = compression_type
    wav_file.getframerate.return_value = sample_rate
    wav_file.readframes.side_effect = audio_chunks

    wav_context = MagicMock()
    wav_context.__enter__.return_value = wav_file
    wav_context.__exit__.return_value = False

    return wav_context, wav_file


def create_recognizer(
    *,
    accepted_results=None,
    intermediate_results=None,
    final_result=None,
):
    if accepted_results is None:
        accepted_results = [False]

    if intermediate_results is None:
        intermediate_results = []

    if final_result is None:
        final_result = json.dumps({"text": ""})

    recognizer = MagicMock()
    recognizer.AcceptWaveform.side_effect = accepted_results
    recognizer.Result.side_effect = intermediate_results
    recognizer.FinalResult.return_value = final_result

    return recognizer


def test_missing_audio_file_does_not_initialize_vosk(
    tmp_path,
):
    audio_path = tmp_path / "missing.wav"
    model_path = create_model_directory(tmp_path)

    with patch.object(
        vosk_transcriber,
        "Model",
    ) as mock_model:
        with pytest.raises(
            FileNotFoundError,
            match="Audio file not found",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()


def test_missing_model_directory_does_not_initialize_vosk(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = tmp_path / "missing-model"

    with patch.object(
        vosk_transcriber,
        "Model",
    ) as mock_model:
        with pytest.raises(
            vosk_transcriber.SpeechModelNotFoundError,
            match="Vosk speech model not found",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()


def test_audio_file_larger_than_ten_mb_is_rejected(
    tmp_path,
):
    audio_path = tmp_path / "oversized.wav"

    with audio_path.open("wb") as audio_file:
        audio_file.truncate(
            vosk_transcriber.MAX_AUDIO_SIZE_BYTES + 1
        )

    model_path = create_model_directory(tmp_path)

    with (
        patch.object(
            vosk_transcriber,
            "wave",
        ) as mock_wave,
        patch.object(
            vosk_transcriber,
            "Model",
        ) as mock_model,
    ):
        with pytest.raises(
            vosk_transcriber.AudioFileTooLargeError,
            match="maximum permitted size of 10 MB",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_wave.open.assert_not_called()
    mock_model.assert_not_called()


@pytest.mark.parametrize(
    "invalid_content",
    [
        b"",
        b"not-a-wave-file",
        b"RIFF-corrupt-data",
    ],
)
def test_invalid_or_corrupt_wav_file_is_rejected(
    tmp_path,
    invalid_content,
):
    audio_path = create_audio_file(
        tmp_path,
        invalid_content,
    )
    model_path = create_model_directory(tmp_path)

    with patch.object(
        vosk_transcriber,
        "Model",
    ) as mock_model:
        with pytest.raises(
            vosk_transcriber.InvalidWavFormatError,
            match="not a valid WAV file",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()


def test_stereo_audio_is_rejected(tmp_path):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context(
        channels=2
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
        ) as mock_model,
    ):
        with pytest.raises(
            vosk_transcriber.InvalidWavFormatError,
            match="exactly one channel",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()
    wav_context.__exit__.assert_called_once()


@pytest.mark.parametrize(
    "sample_width",
    [
        1,
        3,
        4,
    ],
)
def test_non_sixteen_bit_audio_is_rejected(
    tmp_path,
    sample_width,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context(
        sample_width=sample_width
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
        ) as mock_model,
    ):
        with pytest.raises(
            vosk_transcriber.InvalidWavFormatError,
            match="16-bit samples",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()
    wav_context.__exit__.assert_called_once()


def test_compressed_wav_is_rejected(tmp_path):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context(
        compression_type="ULAW"
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
        ) as mock_model,
    ):
        with pytest.raises(
            vosk_transcriber.InvalidWavFormatError,
            match="uncompressed PCM encoding",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()
    wav_context.__exit__.assert_called_once()


@pytest.mark.parametrize(
    "sample_rate",
    [
        0,
        -1,
    ],
)
def test_invalid_sample_rate_is_rejected(
    tmp_path,
    sample_rate,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context(
        sample_rate=sample_rate
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
        ) as mock_model,
    ):
        with pytest.raises(
            vosk_transcriber.InvalidWavFormatError,
            match="positive sample rate",
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    mock_model.assert_not_called()
    wav_context.__exit__.assert_called_once()


def test_vosk_model_and_recognizer_are_initialized_correctly(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context()
    model = MagicMock()
    recognizer = create_recognizer()

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=model,
        ) as mock_model,
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ) as mock_recognizer_class,
    ):
        result = vosk_transcriber.transcribe_wav(
            audio_path,
            model_path,
        )

    assert result == ""
    mock_model.assert_called_once_with(
        str(model_path)
    )
    mock_recognizer_class.assert_called_once_with(
        model,
        16000,
    )


def test_vosk_model_initialization_failure_is_wrapped(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context()

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            side_effect=RuntimeError("model failure"),
        ),
    ):
        with pytest.raises(
            vosk_transcriber.TranscriptionError,
            match="Unable to initialize Vosk transcription",
        ) as error:
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    assert isinstance(
        error.value.__cause__,
        RuntimeError,
    )
    wav_context.__exit__.assert_called_once()


def test_audio_is_processed_in_bounded_chunks(tmp_path):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, wav_file = create_wav_context(
        audio_chunks=[
            b"first-chunk",
            b"second-chunk",
            b"third-chunk",
            b"",
        ]
    )
    recognizer = create_recognizer(
        accepted_results=[
            False,
            False,
            False,
        ]
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
    ):
        result = vosk_transcriber.transcribe_wav(
            audio_path,
            model_path,
        )

    assert result == ""
    assert wav_file.readframes.call_args_list == [
        call(vosk_transcriber.AUDIO_CHUNK_FRAMES),
        call(vosk_transcriber.AUDIO_CHUNK_FRAMES),
        call(vosk_transcriber.AUDIO_CHUNK_FRAMES),
        call(vosk_transcriber.AUDIO_CHUNK_FRAMES),
    ]
    assert recognizer.AcceptWaveform.call_args_list == [
        call(b"first-chunk"),
        call(b"second-chunk"),
        call(b"third-chunk"),
    ]


def test_intermediate_and_final_results_are_combined(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context(
        audio_chunks=[
            b"first-chunk",
            b"second-chunk",
            b"",
        ]
    )
    recognizer = create_recognizer(
        accepted_results=[
            True,
            True,
        ],
        intermediate_results=[
            json.dumps({"text": "good game"}),
            json.dumps({"text": "everyone"}),
        ],
        final_result=json.dumps(
            {"text": "well played"}
        ),
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
    ):
        result = vosk_transcriber.transcribe_wav(
            audio_path,
            model_path,
        )

    assert result == "good game everyone well played"
    assert recognizer.Result.call_count == 2
    recognizer.FinalResult.assert_called_once_with()


def test_empty_speech_results_return_empty_string(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context(
        audio_chunks=[
            b"silence",
            b"",
        ]
    )
    recognizer = create_recognizer(
        accepted_results=[True],
        intermediate_results=[
            json.dumps({"text": "   "})
        ],
        final_result=json.dumps({"text": ""}),
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
    ):
        result = vosk_transcriber.transcribe_wav(
            audio_path,
            model_path,
        )

    assert result == ""


@pytest.mark.parametrize(
    "malformed_result",
    [
        "",
        "{",
        "not-json",
        "[]",
        '{"text": 123}',
    ],
)
def test_malformed_vosk_json_raises_transcription_error(
    tmp_path,
    malformed_result,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context()
    recognizer = create_recognizer(
        accepted_results=[True],
        intermediate_results=[malformed_result],
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
    ):
        with pytest.raises(
            vosk_transcriber.TranscriptionError
        ):
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    wav_context.__exit__.assert_called_once()


def test_recognition_failure_is_wrapped_and_wav_is_closed(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context()
    recognizer = MagicMock()
    recognizer.AcceptWaveform.side_effect = RuntimeError(
        "recognition failure"
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
    ):
        with pytest.raises(
            vosk_transcriber.TranscriptionError,
            match="Vosk transcription failed",
        ) as error:
            vosk_transcriber.transcribe_wav(
                audio_path,
                model_path,
            )

    assert isinstance(
        error.value.__cause__,
        RuntimeError,
    )
    wav_context.__exit__.assert_called_once()


def test_wav_resource_is_closed_after_successful_transcription(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context()
    recognizer = create_recognizer()

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
    ):
        vosk_transcriber.transcribe_wav(
            audio_path,
            model_path,
        )

    wav_context.__enter__.assert_called_once_with()
    wav_context.__exit__.assert_called_once()


def test_importing_module_does_not_initialize_vosk():
    try:
        with patch.object(
            vosk,
            "Model",
        ) as mock_model:
            importlib.reload(vosk_transcriber)
            mock_model.assert_not_called()
    finally:
        importlib.reload(vosk_transcriber)


def test_transcription_never_calls_text_moderation(
    tmp_path,
):
    audio_path = create_audio_file(tmp_path)
    model_path = create_model_directory(tmp_path)
    wav_context, _ = create_wav_context()
    recognizer = create_recognizer(
        accepted_results=[True],
        intermediate_results=[
            json.dumps(
                {"text": "good game everyone"}
            )
        ],
        final_result=json.dumps({"text": ""}),
    )

    with (
        patch.object(
            vosk_transcriber.wave,
            "open",
            return_value=wav_context,
        ),
        patch.object(
            vosk_transcriber,
            "Model",
            return_value=MagicMock(),
        ),
        patch.object(
            vosk_transcriber,
            "KaldiRecognizer",
            return_value=recognizer,
        ),
        patch(
            "src.content_moderation."
            "moderator.moderate_text"
        ) as mock_moderate_text,
    ):
        result = vosk_transcriber.transcribe_wav(
            audio_path,
            model_path,
        )

    assert result == "good game everyone"
    mock_moderate_text.assert_not_called()