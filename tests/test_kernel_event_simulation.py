import copy
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app
from anti_cheat.kernel_event_simulation import (
    SYNTHETIC_EVENT_FIXTURES,
    analyze_simulated_kernel_event,
)


@pytest.fixture
def event():
    return copy.deepcopy(
        SYNTHETIC_EVENT_FIXTURES["normal_process_start"]
    )


TEST_TOKEN = "test-only-kernel-simulation-token"


@pytest.fixture
def client():
    previous_testing = app.config.get("TESTING", False)
    previous_enabled = app.config.get(
        "KERNEL_SIMULATION_ENABLED",
        False,
    )
    previous_token = app.config.get(
        "KERNEL_SIMULATION_API_TOKEN"
    )

    app.config["TESTING"] = True
    app.config["KERNEL_SIMULATION_ENABLED"] = True
    app.config["KERNEL_SIMULATION_API_TOKEN"] = TEST_TOKEN

    try:
        with app.test_client() as test_client:
            yield test_client
    finally:
        app.config["TESTING"] = previous_testing
        app.config["KERNEL_SIMULATION_ENABLED"] = previous_enabled
        app.config["KERNEL_SIMULATION_API_TOKEN"] = previous_token


def authorization_headers(token=TEST_TOKEN):
    return {
        "Authorization": f"Bearer {token}",
    }


def test_valid_normal_event(event):
    result = analyze_simulated_kernel_event(event)

    assert result["classification"] == "NORMAL_PROCESS_ACTIVITY"
    assert result["risk_score"] == 0
    assert result["risk_level"] == "LOW"
    assert result["suspicious"] is False


@pytest.mark.parametrize(
    "event_type,count,classification,score,level",
    [
        (
            "DEBUGGER_ATTACH_ATTEMPT",
            1,
            "PROCESS_TAMPERING_INDICATOR",
            40,
            "MEDIUM",
        ),
        (
            "SUSPICIOUS_LIBRARY_LOAD",
            1,
            "CODE_INJECTION_INDICATOR",
            30,
            "MEDIUM",
        ),
        (
            "REPEATED_PROCESS_ACCESS",
            2,
            "MEMORY_ACCESS_INDICATOR",
            70,
            "HIGH",
        ),
        (
            "PRIVILEGED_ACTIVITY",
            3,
            "PRIVILEGED_ACTIVITY_INDICATOR",
            100,
            "HIGH",
        ),
    ],
)
def test_suspicious_events_and_risk_boundaries(
    event,
    event_type,
    count,
    classification,
    score,
    level,
):
    event["event_type"] = event_type
    event["occurrence_count"] = count
    result = analyze_simulated_kernel_event(event)

    assert result["classification"] == classification
    assert result["risk_score"] == score
    assert result["risk_level"] == level
    assert result["reason_codes"]
    assert result["suspicious"] is True


def test_invalid_event_type(event):
    event["event_type"] = "REAL_KERNEL_EVENT"

    with pytest.raises(ValueError, match="event_type"):
        analyze_simulated_kernel_event(event)


def test_missing_simulation_marker(event):
    del event["simulation"]

    with pytest.raises(ValueError, match="Missing required fields"):
        analyze_simulated_kernel_event(event)


def test_simulation_false(event):
    event["simulation"] = False

    with pytest.raises(ValueError, match="simulation must be true"):
        analyze_simulated_kernel_event(event)


def test_forged_kernel_observed(event):
    event["kernel_observed"] = True

    with pytest.raises(ValueError, match="kernel_observed=true"):
        analyze_simulated_kernel_event(event)


def test_caller_supplied_risk_level(event):
    event["risk_level"] = "LOW"

    with pytest.raises(ValueError, match="risk_level is derived"):
        analyze_simulated_kernel_event(event)


@pytest.mark.parametrize(
    "value",
    [math.nan, math.inf, -math.inf, True, -1, 1.5],
)
def test_invalid_occurrence_counts(event, value):
    event["occurrence_count"] = value

    with pytest.raises(ValueError):
        analyze_simulated_kernel_event(event)


@pytest.mark.parametrize(
    "field,value",
    [
        ("process_identifier", "x" * 129),
        ("event_id", "x" * 65),
    ],
)
def test_oversized_string(event, field, value):
    event[field] = value

    with pytest.raises(ValueError, match=field):
        analyze_simulated_kernel_event(event)


def test_oversized_input(event):
    event["metadata"] = {"description": "x" * 5000}

    with pytest.raises(ValueError, match="encoded bytes"):
        analyze_simulated_kernel_event(event)


def test_unsupported_metadata(event):
    event["metadata"] = {"command_line": "secret"}

    with pytest.raises(ValueError, match="Unsupported metadata"):
        analyze_simulated_kernel_event(event)


def test_unsupported_top_level_field(event):
    event["unexpected"] = "value"

    with pytest.raises(ValueError, match="Unsupported event fields"):
        analyze_simulated_kernel_event(event)


def test_missing_required_field(event):
    del event["event_id"]

    with pytest.raises(ValueError, match="event_id"):
        analyze_simulated_kernel_event(event)


def test_audit_only_behavior(event):
    result = analyze_simulated_kernel_event(event)

    assert result["simulation"] is True
    assert result["kernel_observed"] is False
    assert result["enforcement"] == "DISABLED"
    assert result["decision"] == "AUDIT_ONLY"
    assert "No kernel telemetry was collected" in result["note"]


def test_api_accepts_valid_event(client, event):
    response = client.post(
        "/api/anti-cheat/kernel-simulation/analyze",
        json=event,
        headers=authorization_headers(),
    )

    assert response.status_code == 200
    assert response.get_json()["simulation"] is True


def test_api_rejects_non_json(client):
    response = client.post(
        "/api/anti-cheat/kernel-simulation/analyze",
        data="not json",
        content_type="text/plain",
        headers=authorization_headers(),
    )

    assert response.status_code == 400


def test_api_is_disabled_by_default(client, event):
    app.config["KERNEL_SIMULATION_ENABLED"] = False

    response = client.post(
        "/api/anti-cheat/kernel-simulation/analyze",
        json=event,
        headers=authorization_headers(),
    )

    assert response.status_code == 404


def test_api_fails_closed_without_configured_token(client, event):
    app.config["KERNEL_SIMULATION_API_TOKEN"] = None

    response = client.post(
        "/api/anti-cheat/kernel-simulation/analyze",
        json=event,
        headers=authorization_headers(),
    )

    assert response.status_code == 503
    assert TEST_TOKEN not in response.get_data(as_text=True)


@pytest.mark.parametrize(
    "headers, expected_status",
    [
        ({}, 401),
        ({"Authorization": "Basic credentials"}, 401),
        ({"Authorization": "Bearer"}, 401),
        (authorization_headers("incorrect-token"), 403),
    ],
)
def test_api_rejects_invalid_authorization(
    client,
    event,
    headers,
    expected_status,
):
    response = client.post(
        "/api/anti-cheat/kernel-simulation/analyze",
        json=event,
        headers=headers,
    )

    assert response.status_code == expected_status
    assert TEST_TOKEN not in response.get_data(as_text=True)


def test_api_rejects_oversized_body_before_json_parsing(client):
    oversized_malformed_json = (
        b'{"data":"'
        + b"x" * 8192
        + b'"}'
    )

    response = client.post(
        "/api/anti-cheat/kernel-simulation/analyze",
        data=oversized_malformed_json,
        content_type="application/json",
        headers=authorization_headers(),
    )

    assert response.status_code == 413


def test_no_real_kernel_or_process_interaction(
    monkeypatch,
    event,
):
    def forbidden(*args, **kwargs):
        raise AssertionError("System interaction was attempted")

    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)

    result = analyze_simulated_kernel_event(event)

    assert result["kernel_observed"] is False
    assert result["decision"] == "AUDIT_ONLY"
