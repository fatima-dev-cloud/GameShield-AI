import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

KEY_FILE = BASE_DIR / "config" / "netcode.key"
LOG_FILE = BASE_DIR / "logs" / "infrastructure_security.log"


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def load_or_create_key():
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()

    key = secrets.token_bytes(32)
    KEY_FILE.write_bytes(key)

    return key


def serialize_packet(packet):
    return json.dumps(
        packet,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")


def sign_packet(packet):
    key = load_or_create_key()

    signature = hmac.new(
        key,
        serialize_packet(packet),
        hashlib.sha256
    ).hexdigest()

    return signature


def verify_packet(packet, received_signature):
    expected_signature = sign_packet(packet)

    valid = hmac.compare_digest(
        expected_signature,
        received_signature
    )

    if valid:
        status = "PACKET VERIFIED"

        write_log(
            f"NETCODE_VALID | "
            f"player={packet.get('player_id', 'UNKNOWN')}"
        )

    else:
        status = "PACKET TAMPERING DETECTED"

        write_log(
            f"NETCODE_TAMPERING | "
            f"player={packet.get('player_id', 'UNKNOWN')} | "
            f"action=PACKET_REJECTED"
        )

    return {
        "valid": valid,
        "status": status
    }


if __name__ == "__main__":
    print("=" * 60)
    print("GameShield AI - Secure Game Netcode")
    print("=" * 60)

    original_packet = {
        "player_id": "PLAYER-1001",
        "action": "purchase_item",
        "item_id": "DRAGON-SWORD",
        "price": 2500
    }

    signature = sign_packet(original_packet)

    print("\nOriginal Packet")
    print("-" * 60)
    print(json.dumps(original_packet, indent=4))
    print(f"Signature: {signature[:24]}...")

    valid_result = verify_packet(
        original_packet,
        signature
    )

    print("\nOriginal Packet Verification")
    print("-" * 60)
    print(f"Status: {valid_result['status']}")

    tampered_packet = original_packet.copy()
    tampered_packet["price"] = 1

    tampered_result = verify_packet(
        tampered_packet,
        signature
    )

    print("\nTampered Packet Verification")
    print("-" * 60)
    print("Attacker changed item price: 2500 -> 1")
    print(f"Status: {tampered_result['status']}")