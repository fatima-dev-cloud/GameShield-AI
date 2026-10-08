from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
import threading
import time


BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "infrastructure_security.log"

REQUEST_LIMIT = 10
WINDOW_SECONDS = 10

request_history = defaultdict(deque)
blocked_clients = {}
lock = threading.Lock()


def write_infrastructure_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def check_rate_limit(client_id):
    current_time = time.monotonic()

    with lock:
        blocked_until = blocked_clients.get(client_id)

        if blocked_until is not None:
            if current_time < blocked_until:
                remaining = round(
                    blocked_until - current_time,
                    2
                )

                return {
                    "allowed": False,
                    "status": "CLIENT TEMPORARILY BLOCKED",
                    "remaining_block_seconds": remaining
                }

            blocked_clients.pop(client_id, None)

        history = request_history[client_id]

        while (
            history
            and current_time - history[0] > WINDOW_SECONDS
        ):
            history.popleft()

        if len(history) >= REQUEST_LIMIT:
            block_seconds = 30

            blocked_clients[client_id] = (
                current_time + block_seconds
            )

            write_infrastructure_log(
                f"RATE_LIMIT_TRIGGERED | "
                f"client={client_id} | "
                f"action=TEMPORARY_BLOCK | "
                f"block_seconds={block_seconds}"
            )

            return {
                "allowed": False,
                "status": "RATE LIMIT EXCEEDED",
                "action": "TEMPORARY BLOCK",
                "block_seconds": block_seconds
            }

        history.append(current_time)

        return {
            "allowed": True,
            "status": "REQUEST ALLOWED",
            "requests_in_window": len(history),
            "limit": REQUEST_LIMIT
        }


if __name__ == "__main__":
    print("=" * 60)
    print("GameShield AI - DDoS / Rate Limit Protection")
    print("=" * 60)

    client = "DEMO-CLIENT-001"

    for request_number in range(1, 13):
        result = check_rate_limit(client)

        print(
            f"Request {request_number}: "
            f"{result['status']}"
        )