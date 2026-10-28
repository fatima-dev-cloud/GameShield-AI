from unittest.mock import MagicMock, patch

import pytest

from infrastructure_security import rate_limiter
from src import app as app_module


@pytest.fixture(autouse=True)
def reset_rate_limiter_state():
    with rate_limiter.lock:
        rate_limiter.request_history.clear()
        rate_limiter.blocked_clients.clear()

    yield

    with rate_limiter.lock:
        rate_limiter.request_history.clear()
        rate_limiter.blocked_clients.clear()


@pytest.fixture
def flask_client():
    original_testing = app_module.app.config.get(
        "TESTING"
    )
    original_test_limiter = app_module.app.config.get(
        "TEST_RATE_LIMITER"
    )

    app_module.app.config.update(
        TESTING=True,
        TEST_RATE_LIMITER=True,
    )

    with app_module.app.test_client() as client:
        yield client

    app_module.app.config["TESTING"] = (
        original_testing
    )
    app_module.app.config["TEST_RATE_LIMITER"] = (
        original_test_limiter
    )


def test_first_ten_requests_are_allowed():
    with (
        patch.object(
            rate_limiter.time,
            "monotonic",
            return_value=100.0,
        ),
        patch.object(
            rate_limiter,
            "write_infrastructure_log",
        ) as mock_log,
    ):
        results = [
            rate_limiter.check_rate_limit(
                "client-a"
            )
            for _ in range(
                rate_limiter.REQUEST_LIMIT
            )
        ]

    assert all(
        result["allowed"]
        for result in results
    )
    assert results[-1] == {
        "allowed": True,
        "status": "REQUEST ALLOWED",
        "requests_in_window": 10,
        "limit": rate_limiter.REQUEST_LIMIT,
    }
    mock_log.assert_not_called()


def test_eleventh_request_triggers_temporary_block():
    with (
        patch.object(
            rate_limiter.time,
            "monotonic",
            return_value=100.0,
        ),
        patch.object(
            rate_limiter,
            "write_infrastructure_log",
        ) as mock_log,
    ):
        for _ in range(
            rate_limiter.REQUEST_LIMIT
        ):
            allowed = (
                rate_limiter.check_rate_limit(
                    "client-a"
                )
            )
            assert allowed["allowed"] is True

        denied = rate_limiter.check_rate_limit(
            "client-a"
        )

    assert denied == {
        "allowed": False,
        "status": "RATE LIMIT EXCEEDED",
        "action": "TEMPORARY BLOCK",
        "block_seconds": 30,
    }
    assert (
        rate_limiter.blocked_clients["client-a"]
        == 130.0
    )
    mock_log.assert_called_once_with(
        "RATE_LIMIT_TRIGGERED | "
        "client=client-a | "
        "action=TEMPORARY_BLOCK | "
        "block_seconds=30"
    )


def test_blocked_client_remains_denied_before_expiration():
    rate_limiter.blocked_clients["client-a"] = 130.0

    with (
        patch.object(
            rate_limiter.time,
            "monotonic",
            return_value=110.0,
        ),
        patch.object(
            rate_limiter,
            "write_infrastructure_log",
        ) as mock_log,
    ):
        result = rate_limiter.check_rate_limit(
            "client-a"
        )

    assert result == {
        "allowed": False,
        "status": "CLIENT TEMPORARILY BLOCKED",
        "remaining_block_seconds": 20.0,
    }
    mock_log.assert_not_called()


def test_client_is_allowed_after_block_expires():
    rate_limiter.blocked_clients["client-a"] = 130.0
    rate_limiter.request_history["client-a"].extend(
        [100.0] * rate_limiter.REQUEST_LIMIT
    )

    with (
        patch.object(
            rate_limiter.time,
            "monotonic",
            return_value=131.0,
        ),
        patch.object(
            rate_limiter,
            "write_infrastructure_log",
        ) as mock_log,
    ):
        result = rate_limiter.check_rate_limit(
            "client-a"
        )

    assert result == {
        "allowed": True,
        "status": "REQUEST ALLOWED",
        "requests_in_window": 1,
        "limit": rate_limiter.REQUEST_LIMIT,
    }
    assert "client-a" not in (
        rate_limiter.blocked_clients
    )
    assert list(
        rate_limiter.request_history["client-a"]
    ) == [131.0]
    mock_log.assert_not_called()


def test_old_request_history_is_removed():
    rate_limiter.request_history["client-a"].extend(
        [50.0, 60.0, 95.0]
    )

    with patch.object(
        rate_limiter.time,
        "monotonic",
        return_value=106.0,
    ):
        result = rate_limiter.check_rate_limit(
            "client-a"
        )

    assert result["allowed"] is True
    assert result["requests_in_window"] == 1
    assert list(
        rate_limiter.request_history["client-a"]
    ) == [106.0]


def test_requests_exactly_on_window_boundary_remain():
    rate_limiter.request_history["client-a"].append(
        100.0
    )

    with patch.object(
        rate_limiter.time,
        "monotonic",
        return_value=110.0,
    ):
        result = rate_limiter.check_rate_limit(
            "client-a"
        )

    assert result["allowed"] is True
    assert result["requests_in_window"] == 2
    assert list(
        rate_limiter.request_history["client-a"]
    ) == [100.0, 110.0]


def test_clients_have_independent_request_histories():
    with patch.object(
        rate_limiter.time,
        "monotonic",
        return_value=100.0,
    ):
        for _ in range(
            rate_limiter.REQUEST_LIMIT
        ):
            rate_limiter.check_rate_limit(
                "client-a"
            )

        denied = rate_limiter.check_rate_limit(
            "client-a"
        )
        allowed = rate_limiter.check_rate_limit(
            "client-b"
        )

    assert denied["allowed"] is False
    assert allowed == {
        "allowed": True,
        "status": "REQUEST ALLOWED",
        "requests_in_window": 1,
        "limit": rate_limiter.REQUEST_LIMIT,
    }


def test_flask_request_is_allowed_when_limiter_allows(
    flask_client,
):
    allowed_result = {
        "allowed": True,
        "status": "REQUEST ALLOWED",
        "requests_in_window": 1,
        "limit": rate_limiter.REQUEST_LIMIT,
    }

    with patch.object(
        app_module,
        "check_rate_limit",
        return_value=allowed_result,
    ) as mock_check:
        response = flask_client.get(
            "/api/status",
            environ_base={
                "REMOTE_ADDR": "127.0.0.1"
            },
        )

    assert response.status_code == 200
    assert response.get_json()["status"] == "online"
    mock_check.assert_called_once_with(
        "127.0.0.1"
    )


def test_flask_request_returns_429_when_denied(
    flask_client,
):
    denied_result = {
        "allowed": False,
        "status": "RATE LIMIT EXCEEDED",
        "action": "TEMPORARY BLOCK",
        "block_seconds": 30,
    }

    with patch.object(
        app_module,
        "check_rate_limit",
        return_value=denied_result,
    ) as mock_check:
        response = flask_client.get(
            "/api/status",
            environ_base={
                "REMOTE_ADDR": "127.0.0.1"
            },
        )

    assert response.status_code == 429
    assert response.get_json() == {
        "platform": "GameShield AI",
        "module": "DDoS Protection",
        "error": denied_result,
    }
    mock_check.assert_called_once_with(
        "127.0.0.1"
    )


def test_denied_request_does_not_reach_route_handler(
    flask_client,
):
    endpoint_path = (
        "/api/infrastructure/validate-action"
    )
    denied_result = {
        "allowed": False,
        "status": "RATE LIMIT EXCEEDED",
        "action": "TEMPORARY BLOCK",
        "block_seconds": 30,
    }

    with (
        patch.object(
            app_module,
            "check_rate_limit",
            return_value=denied_result,
        ) as mock_check,
        patch.object(
            app_module,
            "validate_game_action",
        ) as mock_validate,
    ):
        response = flask_client.post(
            endpoint_path,
            json={
                "player_id": "test-player",
                "action": "move",
            },
            environ_base={
                "REMOTE_ADDR": "127.0.0.1"
            },
        )

    assert response.status_code == 429
    mock_check.assert_called_once_with(
        "127.0.0.1"
    )
    mock_validate.assert_not_called()


def test_testing_mode_bypasses_limiter_by_default():
    original_testing = app_module.app.config.get(
        "TESTING"
    )
    original_test_limiter = app_module.app.config.get(
        "TEST_RATE_LIMITER"
    )

    app_module.app.config.update(
        TESTING=True,
        TEST_RATE_LIMITER=False,
    )

    try:
        with (
            app_module.app.test_client() as client,
            patch.object(
                app_module,
                "check_rate_limit",
            ) as mock_check,
        ):
            response = client.get(
                "/api/status",
                environ_base={
                    "REMOTE_ADDR": "127.0.0.1"
                },
            )

        assert response.status_code == 200
        mock_check.assert_not_called()
    finally:
        app_module.app.config["TESTING"] = (
            original_testing
        )
        app_module.app.config[
            "TEST_RATE_LIMITER"
        ] = original_test_limiter


def test_static_endpoint_bypasses_limiter(
    flask_client,
):
    with patch.object(
        app_module,
        "check_rate_limit",
    ) as mock_check:
        response = flask_client.get(
            "/static/missing-file.css",
            environ_base={
                "REMOTE_ADDR": "127.0.0.1"
            },
        )

    assert response.status_code == 404
    mock_check.assert_not_called()


def test_unknown_client_fallback_is_used(
    flask_client,
):
    allowed_result = {
        "allowed": True,
        "status": "REQUEST ALLOWED",
        "requests_in_window": 1,
        "limit": rate_limiter.REQUEST_LIMIT,
    }

    with (
        app_module.app.test_request_context(
            "/api/status"
        ),
        patch.object(
            app_module,
            "check_rate_limit",
            return_value=allowed_result,
        ) as mock_check,
    ):
        result = (
            app_module.infrastructure_rate_limit()
        )

    assert result is None
    mock_check.assert_called_once_with(
        "UNKNOWN"
    )