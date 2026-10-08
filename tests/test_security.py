import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anti_cheat.detector import analyze_player
from asset_security.fraud_detector import analyze_transaction
from identity_security.authentication import (
    hash_password,
    verify_password,
)
from infrastructure_security.secure_netcode import (
    sign_packet,
    verify_packet,
)
from infrastructure_security.server_validation import (
    validate_game_action,
)
from content_moderation.child_safety import (
    check_age_appropriate_content,
)


def test_anti_cheat_detects_suspicious_player():
    player = {
        "accuracy": 0.98,
        "headshot_rate": 0.95,
        "reaction_time": 40,
        "kills_per_minute": 7.5,
        "impossible_actions": 15,
        "tracking_score": 0.99,
    }

    result = analyze_player(player)

    assert result["prediction"] == 1
    assert result["status"] == "CHEATER DETECTED"


def test_marketplace_blocks_fraud():
    transaction = {
        "transaction_id": "TEST-FRAUD-001",
        "amount": 7500,
        "transactions_last_minute": 12,
        "account_age_days": 1,
        "different_country": True,
        "asset_value": 8000,
    }

    result = analyze_transaction(transaction)

    assert result["decision"] == "BLOCKED"
    assert result["risk_level"] == "HIGH"


def test_password_hashing():
    password = "TestPassword@2026"

    salt, password_hash = hash_password(password)

    assert password not in password_hash

    assert verify_password(
        password,
        salt,
        password_hash,
    )

    assert not verify_password(
        "WrongPassword",
        salt,
        password_hash,
    )


def test_packet_tampering_detection():
    packet = {
        "player_id": "TEST-PLAYER",
        "action": "purchase_item",
        "price": 2500,
    }

    signature = sign_packet(packet)

    assert verify_packet(packet, signature)["valid"]

    tampered = packet.copy()
    tampered["price"] = 1

    assert not verify_packet(
        tampered,
        signature,
    )["valid"]


def test_server_rejects_impossible_actions():
    action = {
        "player_id": "TEST-PLAYER",
        "movement_speed": 80,
        "damage": 999,
        "fire_rate": 30,
    }

    result = validate_game_action(action)

    assert result["valid"] is False
    assert result["status"] == "ACTION REJECTED"


def test_child_safety_blocks_underage_user():
    result = check_age_appropriate_content(
        12,
        "MATURE",
    )

    assert result["access"] == "BLOCKED"


def test_child_safety_allows_appropriate_content():
    result = check_age_appropriate_content(
        12,
        "EVERYONE",
    )

    assert result["access"] == "ALLOWED"