import json
import math
import statistics
import sys
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any, TextIO

from src.content_moderation.moderator import (
    moderate_text,
)
from src.voice_moderation.voice_moderator import (
    moderate_voice,
)


DEFAULT_LIMITATIONS = [
    (
        "Results apply only to the explicitly labeled local "
        "samples supplied to this benchmark."
    ),
    (
        "A small or synthetic sample set is not representative "
        "of production traffic."
    ),
    (
        "Sample labels may involve human judgment and should be "
        "reviewed before conclusions are drawn."
    ),
    (
        "False-positive and false-negative rates from this run "
        "are not general model accuracy guarantees."
    ),
    (
        "Rejected or otherwise unclassified inputs are excluded "
        "from false-positive and false-negative calculations."
    ),
    (
        "Voice results depend on the speaker, microphone, noise, "
        "WAV encoding, and selected Vosk model."
    ),
    (
        "Latency depends on instance type, current system load, "
        "filesystem performance, and model caching."
    ),
    (
        "The first invocation may include model-loading overhead; "
        "later invocations may benefit from warmed caches."
    ),
    (
        "Text and voice latency are not directly comparable unless "
        "their execution conditions are equivalent."
    ),
    (
        "This benchmark does not establish production performance, "
        "capacity, security, or availability guarantees."
    ),
]


def _validate_positive_integer(
    value: Any,
    name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{name} must be an integer"
        )

    if value < 1:
        raise ValueError(
            f"{name} must be at least 1"
        )

    return value


def _normalize_labeled_messages(
    labeled_messages: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(
        labeled_messages,
        (str, bytes, Mapping),
    ):
        raise TypeError(
            "labeled_messages must be an iterable of mappings"
        )

    try:
        supplied_messages = list(labeled_messages)
    except TypeError as exc:
        raise TypeError(
            "labeled_messages must be an iterable of mappings"
        ) from exc

    normalized_messages = []

    for index, sample in enumerate(supplied_messages):
        if not isinstance(sample, Mapping):
            raise TypeError(
                f"Sample {index} must be a mapping"
            )

        if "text" not in sample:
            raise ValueError(
                f"Sample {index} is missing text"
            )

        if "expected_toxic" not in sample:
            raise ValueError(
                f"Sample {index} is missing expected_toxic"
            )

        text = sample["text"]
        expected_toxic = sample["expected_toxic"]

        if not isinstance(text, str):
            raise TypeError(
                f"Sample {index} text must be a string"
            )

        if type(expected_toxic) is not bool:
            raise TypeError(
                f"Sample {index} expected_toxic must be a boolean"
            )

        normalized_messages.append({
            "text": text,
            "expected_toxic": expected_toxic,
        })

    if not normalized_messages:
        raise ValueError(
            "At least one labeled message is required"
        )

    return normalized_messages


def _predicted_toxicity(
    moderation_result: Any,
) -> bool | None:
    if not isinstance(moderation_result, Mapping):
        raise TypeError(
            "Moderation results must be mappings"
        )

    status = moderation_result.get("status")
    action = moderation_result.get("action")

    if (
        status == "TOXIC CONTENT DETECTED"
        and action == "BLOCK"
    ):
        return True

    if (
        status == "CONTENT SAFE"
        and action == "ALLOW"
    ):
        return False

    return None


def _measure_call(
    function: Callable[[], Any],
    clock: Callable[[], float],
) -> tuple[Any, float]:
    started_at = clock()
    result = function()
    finished_at = clock()

    elapsed = finished_at - started_at

    if elapsed < 0:
        raise ValueError(
            "Benchmark clock moved backwards"
        )

    return result, elapsed


def summarize_latencies(
    latencies: Iterable[float],
) -> dict[str, Any]:
    values = list(latencies)

    for latency in values:
        if isinstance(latency, bool) or not isinstance(
            latency,
            (int, float),
        ):
            raise TypeError(
                "Latency values must be numeric"
            )

        if latency < 0:
            raise ValueError(
                "Latency values cannot be negative"
            )

    if not values:
        return {
            "runs": 0,
            "minimum_seconds": None,
            "maximum_seconds": None,
            "mean_seconds": None,
            "median_seconds": None,
            "p95_seconds": None,
        }

    sorted_values = sorted(float(value) for value in values)
    p95_index = max(
        0,
        math.ceil(0.95 * len(sorted_values)) - 1,
    )

    return {
        "runs": len(sorted_values),
        "minimum_seconds": min(sorted_values),
        "maximum_seconds": max(sorted_values),
        "mean_seconds": statistics.fmean(
            sorted_values
        ),
        "median_seconds": statistics.median(
            sorted_values
        ),
        "p95_seconds": sorted_values[p95_index],
    }


def _latency_report(
    latencies: list[float],
) -> dict[str, Any]:
    return {
        "first_run_seconds": (
            latencies[0]
            if latencies
            else None
        ),
        "warm_runs": summarize_latencies(
            latencies[1:]
        ),
        "all_runs": summarize_latencies(
            latencies
        ),
    }


def _calculate_rate(
    numerator: int,
    denominator: int,
) -> float | None:
    if denominator == 0:
        return None

    return numerator / denominator


def benchmark_text_moderation(
    labeled_messages: Iterable[Mapping[str, Any]],
    *,
    moderation_function: Callable[[str], Mapping[str, Any]] = (
        moderate_text
    ),
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, Any]:
    samples = _normalize_labeled_messages(
        labeled_messages
    )

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    excluded_samples = 0
    latencies = []

    for sample in samples:
        result, latency = _measure_call(
            lambda sample_text=sample["text"]: (
                moderation_function(sample_text)
            ),
            clock,
        )
        latencies.append(latency)

        prediction = _predicted_toxicity(result)

        if prediction is None:
            excluded_samples += 1
            continue

        expected_toxic = sample["expected_toxic"]

        if expected_toxic and prediction:
            true_positives += 1
        elif not expected_toxic and not prediction:
            true_negatives += 1
        elif not expected_toxic and prediction:
            false_positives += 1
        else:
            false_negatives += 1

    expected_toxic_count = sum(
        1
        for sample in samples
        if sample["expected_toxic"]
    )
    expected_safe_count = (
        len(samples) - expected_toxic_count
    )
    evaluated_samples = (
        len(samples) - excluded_samples
    )

    return {
        "sample_size": len(samples),
        "expected_safe_samples": expected_safe_count,
        "expected_toxic_samples": expected_toxic_count,
        "evaluated_samples": evaluated_samples,
        "excluded_samples": excluded_samples,
        "confusion_matrix": {
            "true_positives": true_positives,
            "true_negatives": true_negatives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        },
        "false_positive_rate": _calculate_rate(
            false_positives,
            false_positives + true_negatives,
        ),
        "false_negative_rate": _calculate_rate(
            false_negatives,
            false_negatives + true_positives,
        ),
        "latency": _latency_report(latencies),
    }


def benchmark_voice_moderation(
    audio_file: Any,
    model_path: Any,
    *,
    runs: int = 1,
    voice_function: Callable[[Any, Any], Mapping[str, Any]] = (
        moderate_voice
    ),
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, Any]:
    run_count = _validate_positive_integer(
        runs,
        "runs",
    )

    latencies = []
    empty_transcriptions = 0

    for _ in range(run_count):
        result, latency = _measure_call(
            lambda: voice_function(
                audio_file,
                model_path,
            ),
            clock,
        )

        if not isinstance(result, Mapping):
            raise TypeError(
                "Voice moderation results must be mappings"
            )

        transcript = result.get("transcription")

        if not isinstance(transcript, str):
            raise TypeError(
                "Voice moderation transcription must be a string"
            )

        if transcript == "":
            empty_transcriptions += 1

        latencies.append(latency)

    return {
        "runs": run_count,
        "successful_runs": run_count,
        "empty_transcriptions": empty_transcriptions,
        "latency": _latency_report(latencies),
    }


def build_benchmark_report(
    labeled_messages: Iterable[Mapping[str, Any]],
    audio_file: Any,
    model_path: Any,
    *,
    voice_runs: int = 1,
    text_function: Callable[[str], Mapping[str, Any]] = (
        moderate_text
    ),
    voice_function: Callable[[Any, Any], Mapping[str, Any]] = (
        moderate_voice
    ),
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, Any]:
    text_report = benchmark_text_moderation(
        labeled_messages,
        moderation_function=text_function,
        clock=clock,
    )
    voice_report = benchmark_voice_moderation(
        audio_file,
        model_path,
        runs=voice_runs,
        voice_function=voice_function,
        clock=clock,
    )

    return {
        "benchmark": "GameShield AI Day 5 Moderation Benchmark",
        "text_moderation": text_report,
        "voice_moderation": voice_report,
        "limitations": list(DEFAULT_LIMITATIONS),
    }


def print_benchmark_report(
    report: Mapping[str, Any],
    *,
    stream: TextIO | None = None,
) -> None:
    if not isinstance(report, Mapping):
        raise TypeError(
            "report must be a mapping"
        )

    output_stream = (
        stream
        if stream is not None
        else sys.stdout
    )

    json.dump(
        report,
        output_stream,
        indent=2,
        sort_keys=True,
    )
    output_stream.write("\n")


def run_benchmark(
    labeled_messages: Iterable[Mapping[str, Any]],
    audio_file: Any,
    model_path: Any,
    *,
    voice_runs: int = 1,
    text_function: Callable[[str], Mapping[str, Any]] = (
        moderate_text
    ),
    voice_function: Callable[[Any, Any], Mapping[str, Any]] = (
        moderate_voice
    ),
    clock: Callable[[], float] = time.perf_counter,
    stream: TextIO | None = None,
) -> dict[str, Any]:
    report = build_benchmark_report(
        labeled_messages,
        audio_file,
        model_path,
        voice_runs=voice_runs,
        text_function=text_function,
        voice_function=voice_function,
        clock=clock,
    )

    print_benchmark_report(
        report,
        stream=stream,
    )

    return report