"""
Safe user-space simulation of kernel-like anti-cheat events.

No kernel telemetry is collected and no enforcement is performed.
"""

from datetime import datetime, timezone
import json
import math


SCHEMA_VERSION = "1.0"
MAX_EVENT_SIZE_BYTES = 4096
MAX_OCCURRENCE_COUNT = 100

ALLOWED_SIMULATED_SOURCES = {
    "demo_api",
    "educational_fixture",
}

EVENT_RULES = {
    "PROCESS_START": (
        "NORMAL_PROCESS_ACTIVITY",
        0,
        "SIMULATED_NORMAL_PROCESS_START",
    ),
    "DEBUGGER_ATTACH_ATTEMPT": (
        "PROCESS_TAMPERING_INDICATOR",
        40,
        "SIMULATED_DEBUGGER_ATTACH",
    ),
    "SUSPICIOUS_LIBRARY_LOAD": (
        "CODE_INJECTION_INDICATOR",
        30,
        "SIMULATED_SUSPICIOUS_LIBRARY_LOAD",
    ),
    "REPEATED_PROCESS_ACCESS": (
        "MEMORY_ACCESS_INDICATOR",
        35,
        "SIMULATED_REPEATED_PROCESS_ACCESS",
    ),
    "PRIVILEGED_ACTIVITY": (
        "PRIVILEGED_ACTIVITY_INDICATOR",
        50,
        "SIMULATED_PRIVILEGED_ACTIVITY",
    ),
}

REQUIRED_FIELDS = {
    "schema_version",
    "event_id",
    "event_type",
    "timestamp",
    "process_identifier",
    "occurrence_count",
    "simulated_source",
    "simulation",
}

ALLOWED_FIELDS = REQUIRED_FIELDS | {
    "metadata",
    "target_identifier",
}

STRING_LIMITS = {
    "event_id": 64,
    "process_identifier": 128,
    "target_identifier": 128,
}

METADATA_LIMITS = {
    "description": 256,
    "fixture_name": 128,
}

EDUCATIONAL_LIMITATION = (
    "Synthetic educational event only. No kernel telemetry was "
    "collected, no cheating was proven, and no enforcement occurred."
)

SYNTHETIC_EVENT_FIXTURES = {
    "normal_process_start": {
        "schema_version": SCHEMA_VERSION,
        "event_id": "fixture-normal-001",
        "event_type": "PROCESS_START",
        "timestamp": "2026-10-26T10:00:00Z",
        "process_identifier": "game-client-demo",
        "occurrence_count": 1,
        "simulated_source": "educational_fixture",
        "simulation": True,
        "metadata": {
            "fixture_name": "normal_process_start",
        },
    },
    "simulated_debugger_attempt": {
        "schema_version": SCHEMA_VERSION,
        "event_id": "fixture-debugger-001",
        "event_type": "DEBUGGER_ATTACH_ATTEMPT",
        "timestamp": "2026-10-26T10:01:00Z",
        "process_identifier": "debugger-demo",
        "target_identifier": "game-client-demo",
        "occurrence_count": 1,
        "simulated_source": "educational_fixture",
        "simulation": True,
        "metadata": {
            "fixture_name": "simulated_debugger_attempt",
        },
    },
}


def _validate_string(event, field, required=True):
    value = event.get(field)

    if value is None and not required:
        return

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")

    if len(value) > STRING_LIMITS[field]:
        raise ValueError(
            f"{field} exceeds {STRING_LIMITS[field]} characters"
        )


def _validate_timestamp(value):
    if (
        not isinstance(value, str)
        or len(value) > 32
        or "T" not in value
    ):
        raise ValueError(
            "timestamp must be a bounded ISO 8601 timestamp"
        )

    if not value.endswith("Z"):
        raise ValueError(
            "timestamp must use ISO 8601 UTC format ending in Z"
        )

    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        raise ValueError(
            "timestamp must be a valid ISO 8601 UTC value"
        ) from None

    if parsed.tzinfo != timezone.utc:
        raise ValueError("timestamp must use UTC")


def _validate_occurrence_count(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            "occurrence_count must be a finite integer"
        )

    if not math.isfinite(value) or not float(value).is_integer():
        raise ValueError(
            "occurrence_count must be a finite integer"
        )

    value = int(value)

    if not 1 <= value <= MAX_OCCURRENCE_COUNT:
        raise ValueError(
            "occurrence_count must be between 1 and "
            f"{MAX_OCCURRENCE_COUNT}"
        )

    return value


def _validate_metadata(value):
    if value is None:
        return {}

    if not isinstance(value, dict):
        raise ValueError("metadata must be a JSON object")

    unsupported = set(value) - set(METADATA_LIMITS)

    if unsupported:
        raise ValueError(
            "Unsupported metadata fields: "
            + ", ".join(sorted(unsupported))
        )

    for field, item in value.items():
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"metadata.{field} must be a non-empty string"
            )

        if len(item) > METADATA_LIMITS[field]:
            raise ValueError(
                f"metadata.{field} exceeds "
                f"{METADATA_LIMITS[field]} characters"
            )

    return dict(value)


def validate_simulated_event(event):
    if not isinstance(event, dict):
        raise ValueError("Event must be a JSON object")

    if "risk_level" in event:
        raise ValueError(
            "risk_level is derived and cannot be supplied"
        )

    if event.get("kernel_observed") is True:
        raise ValueError(
            "kernel_observed=true is forbidden for simulations"
        )

    unsupported = set(event) - ALLOWED_FIELDS

    if unsupported:
        raise ValueError(
            "Unsupported event fields: "
            + ", ".join(sorted(unsupported))
        )

    missing = REQUIRED_FIELDS - set(event)

    if missing:
        raise ValueError(
            "Missing required fields: "
            + ", ".join(sorted(missing))
        )

    try:
        encoded_size = len(
            json.dumps(
                event,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    except (TypeError, ValueError, OverflowError):
        raise ValueError(
            "Event must contain JSON-compatible values"
        ) from None

    if encoded_size > MAX_EVENT_SIZE_BYTES:
        raise ValueError(
            f"Event exceeds {MAX_EVENT_SIZE_BYTES} encoded bytes"
        )

    if event["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"schema_version must be {SCHEMA_VERSION}"
        )

    if event["simulation"] is not True:
        raise ValueError("simulation must be true")

    source = event["simulated_source"]

    if (
        not isinstance(source, str)
        or source not in ALLOWED_SIMULATED_SOURCES
    ):
        raise ValueError("simulated_source is not allowed")

    event_type = event["event_type"]

    if (
        not isinstance(event_type, str)
        or event_type not in EVENT_RULES
    ):
        raise ValueError("event_type is not supported")

    _validate_string(event, "event_id")
    _validate_string(event, "process_identifier")
    _validate_string(
        event,
        "target_identifier",
        required=False,
    )
    _validate_timestamp(event["timestamp"])

    validated = dict(event)
    validated["occurrence_count"] = _validate_occurrence_count(
        event["occurrence_count"]
    )
    validated["metadata"] = _validate_metadata(
        event.get("metadata")
    )

    return validated


def analyze_simulated_kernel_event(event):
    event = validate_simulated_event(event)
    classification, points, reason_code = EVENT_RULES[
        event["event_type"]
    ]
    risk_score = min(
        points * event["occurrence_count"],
        100,
    )

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "module": "Simulated Kernel-Event Anti-Cheat",
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "classification": classification,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reason_codes": [reason_code],
        "suspicious": risk_score >= 30,
        "simulation": True,
        "simulated_source": event["simulated_source"],
        "kernel_observed": False,
        "enforcement": "DISABLED",
        "decision": "AUDIT_ONLY",
        "note": EDUCATIONAL_LIMITATION,
    }
