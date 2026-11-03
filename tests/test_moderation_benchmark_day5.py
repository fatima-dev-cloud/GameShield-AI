import io
import json
from unittest.mock import MagicMock, call

import pytest

from src.evaluation import moderation_benchmark


SAFE_RESULT = {
    "status": "CONTENT SAFE",
    "action": "ALLOW",
    "risk_level": "LOW",
    "toxicity_probability": 10.0,
}

TOXIC_RESULT = {
    "status": "TOXIC CONTENT DETECTED",
    "action": "BLOCK",
    "risk_level": "HIGH",
    "toxicity_probability": 80.0,
}

REJECTED_RESULT = {
    "status": "REJECTED",
    "action": "BLOCK",
    "reason": "Empty message",
    "toxicity_probability": 0.0,
}


def clock_with_values(*values):
    return MagicMock(
        side_effect=values
    )


def test_latency_summary_is_calculated_correctly():
    result = moderation_benchmark.summarize_latencies(
        [0.4, 0.1, 0.2, 0.3]
    )

    assert result == {
        "runs": 4,
        "minimum_seconds": 0.1,
        "maximum_seconds": 0.4,
        "mean_seconds": pytest.approx(0.25),
        "median_seconds": pytest.approx(0.25),
        "p95_seconds": 0.4,
    }


def test_empty_latency_summary_uses_none_values():
    result = moderation_benchmark.summarize_latencies(
        []
    )

    assert result == {
        "runs": 0,
        "minimum_seconds": None,
        "maximum_seconds": None,
        "mean_seconds": None,
        "median_seconds": None,
        "p95_seconds": None,
    }


@pytest.mark.parametrize(
    "invalid_latency",
    [
        -0.1,
        True,
        "0.1",
        None,
    ],
)
def test_invalid_latency_values_are_rejected(
    invalid_latency,
):
    expected_exception = (
        ValueError
        if isinstance(invalid_latency, (int, float))
        and not isinstance(invalid_latency, bool)
        else TypeError
    )

    with pytest.raises(expected_exception):
        moderation_benchmark.summarize_latencies(
            [invalid_latency]
        )


def test_text_benchmark_calculates_confusion_matrix():
    labeled_messages = [
        {
            "text": "safe true negative",
            "expected_toxic": False,
        },
        {
            "text": "toxic true positive",
            "expected_toxic": True,
        },
        {
            "text": "safe false positive",
            "expected_toxic": False,
        },
        {
            "text": "toxic false negative",
            "expected_toxic": True,
        },
    ]

    moderation_function = MagicMock(
        side_effect=[
            SAFE_RESULT,
            TOXIC_RESULT,
            TOXIC_RESULT,
            SAFE_RESULT,
        ]
    )
    clock = clock_with_values(
        0.0,
        0.1,
        1.0,
        1.2,
        2.0,
        2.3,
        3.0,
        3.4,
    )

    result = (
        moderation_benchmark
        .benchmark_text_moderation(
            labeled_messages,
            moderation_function=moderation_function,
            clock=clock,
        )
    )

    assert result["sample_size"] == 4
    assert result["expected_safe_samples"] == 2
    assert result["expected_toxic_samples"] == 2
    assert result["evaluated_samples"] == 4
    assert result["excluded_samples"] == 0
    assert result["confusion_matrix"] == {
        "true_positives": 1,
        "true_negatives": 1,
        "false_positives": 1,
        "false_negatives": 1,
    }
    assert result["false_positive_rate"] == 0.5
    assert result["false_negative_rate"] == 0.5

    assert moderation_function.call_args_list == [
        call("safe true negative"),
        call("toxic true positive"),
        call("safe false positive"),
        call("toxic false negative"),
    ]
    assert moderation_function.call_count == 4

    latency = result["latency"]
    assert latency["first_run_seconds"] == 0.1
    assert latency["all_runs"]["runs"] == 4
    assert latency["warm_runs"]["runs"] == 3


def test_rejected_samples_are_excluded_from_rates():
    moderation_function = MagicMock(
        side_effect=[
            REJECTED_RESULT,
            SAFE_RESULT,
        ]
    )
    clock = clock_with_values(
        0.0,
        0.1,
        1.0,
        1.2,
    )

    result = (
        moderation_benchmark
        .benchmark_text_moderation(
            [
                {
                    "text": "",
                    "expected_toxic": False,
                },
                {
                    "text": "safe",
                    "expected_toxic": False,
                },
            ],
            moderation_function=moderation_function,
            clock=clock,
        )
    )

    assert result["sample_size"] == 2
    assert result["evaluated_samples"] == 1
    assert result["excluded_samples"] == 1
    assert result["confusion_matrix"] == {
        "true_positives": 0,
        "true_negatives": 1,
        "false_positives": 0,
        "false_negatives": 0,
    }
    assert result["false_positive_rate"] == 0.0
    assert result["false_negative_rate"] is None


def test_zero_safe_denominator_returns_none():
    moderation_function = MagicMock(
        return_value=TOXIC_RESULT
    )
    clock = clock_with_values(0.0, 0.1)

    result = (
        moderation_benchmark
        .benchmark_text_moderation(
            [
                {
                    "text": "toxic",
                    "expected_toxic": True,
                }
            ],
            moderation_function=moderation_function,
            clock=clock,
        )
    )

    assert result["false_positive_rate"] is None
    assert result["false_negative_rate"] == 0.0


def test_zero_toxic_denominator_returns_none():
    moderation_function = MagicMock(
        return_value=SAFE_RESULT
    )
    clock = clock_with_values(0.0, 0.1)

    result = (
        moderation_benchmark
        .benchmark_text_moderation(
            [
                {
                    "text": "safe",
                    "expected_toxic": False,
                }
            ],
            moderation_function=moderation_function,
            clock=clock,
        )
    )

    assert result["false_positive_rate"] == 0.0
    assert result["false_negative_rate"] is None


@pytest.mark.parametrize(
    ("samples", "exception_type"),
    [
        ([], ValueError),
        ("not-a-sample-list", TypeError),
        ([{"expected_toxic": False}], ValueError),
        ([{"text": "message"}], ValueError),
        (
            [{
                "text": 123,
                "expected_toxic": False,
            }],
            TypeError,
        ),
        (
            [{
                "text": "message",
                "expected_toxic": 1,
            }],
            TypeError,
        ),
        ([None], TypeError),
    ],
)
def test_invalid_labeled_samples_are_rejected(
    samples,
    exception_type,
):
    with pytest.raises(exception_type):
        (
            moderation_benchmark
            .benchmark_text_moderation(
                samples,
                moderation_function=MagicMock(),
            )
        )


def test_clock_moving_backwards_is_rejected():
    clock = clock_with_values(2.0, 1.0)

    with pytest.raises(
        ValueError,
        match="Benchmark clock moved backwards",
    ):
        (
            moderation_benchmark
            .benchmark_text_moderation(
                [{
                    "text": "safe",
                    "expected_toxic": False,
                }],
                moderation_function=MagicMock(
                    return_value=SAFE_RESULT
                ),
                clock=clock,
            )
        )


def test_voice_benchmark_forwards_paths_and_counts_runs():
    audio_path = (
        "/tmp/gameshield-audio-test/"
        "test_voice.wav"
    )
    model_path = (
        "models/vosk/"
        "vosk-model-small-en-us-0.15"
    )

    voice_function = MagicMock(
        side_effect=[
            {
                "transcription": "good game",
                "moderation": SAFE_RESULT,
            },
            {
                "transcription": "good game",
                "moderation": SAFE_RESULT,
            },
        ]
    )
    clock = clock_with_values(
        0.0,
        0.5,
        1.0,
        1.2,
    )

    result = (
        moderation_benchmark
        .benchmark_voice_moderation(
            audio_path,
            model_path,
            runs=2,
            voice_function=voice_function,
            clock=clock,
        )
    )

    assert result["runs"] == 2
    assert result["successful_runs"] == 2
    assert result["empty_transcriptions"] == 0
    assert result["latency"]["first_run_seconds"] == 0.5
    assert (
        result["latency"]["warm_runs"]
        ["mean_seconds"]
        == pytest.approx(0.2)
    )

    assert voice_function.call_args_list == [
        call(audio_path, model_path),
        call(audio_path, model_path),
    ]


def test_voice_benchmark_counts_empty_transcriptions():
    voice_function = MagicMock(
        return_value={
            "transcription": "",
            "moderation": REJECTED_RESULT,
        }
    )
    clock = clock_with_values(0.0, 0.1)

    result = (
        moderation_benchmark
        .benchmark_voice_moderation(
            "audio.wav",
            "model",
            voice_function=voice_function,
            clock=clock,
        )
    )

    assert result["empty_transcriptions"] == 1


@pytest.mark.parametrize(
    "invalid_runs",
    [
        0,
        -1,
        True,
        1.5,
        "2",
    ],
)
def test_invalid_voice_run_count_is_rejected(
    invalid_runs,
):
    expected_exception = (
        ValueError
        if isinstance(invalid_runs, int)
        and not isinstance(invalid_runs, bool)
        else TypeError
    )

    with pytest.raises(expected_exception):
        (
            moderation_benchmark
            .benchmark_voice_moderation(
                "audio.wav",
                "model",
                runs=invalid_runs,
                voice_function=MagicMock(),
            )
        )


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        [],
        "transcript",
        {"transcription": None},
        {"transcription": 123},
    ],
)
def test_invalid_voice_results_are_rejected(
    invalid_result,
):
    voice_function = MagicMock(
        return_value=invalid_result
    )
    clock = clock_with_values(0.0, 0.1)

    with pytest.raises(TypeError):
        (
            moderation_benchmark
            .benchmark_voice_moderation(
                "audio.wav",
                "model",
                voice_function=voice_function,
                clock=clock,
            )
        )


def test_complete_report_contains_limitations():
    text_function = MagicMock(
        return_value=SAFE_RESULT
    )
    voice_function = MagicMock(
        return_value={
            "transcription": "safe speech",
            "moderation": SAFE_RESULT,
        }
    )
    clock = clock_with_values(
        0.0,
        0.1,
        1.0,
        1.5,
    )

    report = (
        moderation_benchmark
        .build_benchmark_report(
            [{
                "text": "safe text",
                "expected_toxic": False,
            }],
            "audio.wav",
            "model",
            text_function=text_function,
            voice_function=voice_function,
            clock=clock,
        )
    )

    assert report["benchmark"] == (
        "GameShield AI Day 5 "
        "Moderation Benchmark"
    )
    assert report["limitations"] == (
        moderation_benchmark.DEFAULT_LIMITATIONS
    )
    assert report["text_moderation"]["sample_size"] == 1
    assert report["voice_moderation"]["runs"] == 1


def test_report_does_not_contain_messages_or_transcripts():
    raw_message = "PRIVATE LABELED MESSAGE"
    transcript = "PRIVATE SPOKEN TRANSCRIPT"

    text_function = MagicMock(
        return_value=SAFE_RESULT
    )
    voice_function = MagicMock(
        return_value={
            "transcription": transcript,
            "moderation": SAFE_RESULT,
        }
    )
    clock = clock_with_values(
        0.0,
        0.1,
        1.0,
        1.5,
    )

    report = (
        moderation_benchmark
        .build_benchmark_report(
            [{
                "text": raw_message,
                "expected_toxic": False,
            }],
            "/private/audio/path.wav",
            "/private/model/path",
            text_function=text_function,
            voice_function=voice_function,
            clock=clock,
        )
    )

    serialized = json.dumps(report)

    assert raw_message not in serialized
    assert transcript not in serialized
    assert "/private/audio/path.wav" not in serialized
    assert "/private/model/path" not in serialized


def test_print_report_writes_json_to_supplied_stream():
    stream = io.StringIO()
    report = {
        "benchmark": "local",
        "limitations": ["sample limitation"],
    }

    moderation_benchmark.print_benchmark_report(
        report,
        stream=stream,
    )

    assert json.loads(stream.getvalue()) == report
    assert stream.getvalue().endswith("\n")


def test_run_benchmark_prints_stdout_only(capsys):
    text_function = MagicMock(
        return_value=SAFE_RESULT
    )
    voice_function = MagicMock(
        return_value={
            "transcription": "safe speech",
            "moderation": SAFE_RESULT,
        }
    )
    clock = clock_with_values(
        0.0,
        0.1,
        1.0,
        1.2,
    )

    report = moderation_benchmark.run_benchmark(
        [{
            "text": "safe sample",
            "expected_toxic": False,
        }],
        "audio.wav",
        "model",
        text_function=text_function,
        voice_function=voice_function,
        clock=clock,
    )

    captured = capsys.readouterr()
    printed_report = json.loads(captured.out)

    assert captured.err == ""
    assert printed_report == report