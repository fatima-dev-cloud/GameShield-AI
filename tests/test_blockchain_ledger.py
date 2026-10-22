
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
ASSET_DIR = SRC_DIR / "asset_security"

for directory in (SRC_DIR, ASSET_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from asset_security import blockchain_ledger


def sample_assets():
    from asset_security.asset_registry import create_asset_hash

    first = {
        "asset_id": "ASSET-001",
        "asset_name": "Dragon Sword",
        "owner_id": "PLAYER-001",
        "created_at": "2026-01-01T00:00:00+00:00",
        "previous_hash": "GENESIS",
    }

    first["asset_hash"] = create_asset_hash(
        first["asset_id"],
        first["asset_name"],
        first["owner_id"],
        first["created_at"],
        first["previous_hash"],
    )

    second = {
        "asset_id": "ASSET-002",
        "asset_name": "Golden Shield",
        "owner_id": "PLAYER-002",
        "created_at": "2026-01-02T00:00:00+00:00",
        "previous_hash": first["asset_hash"],
    }

    second["asset_hash"] = create_asset_hash(
        second["asset_id"],
        second["asset_name"],
        second["owner_id"],
        second["created_at"],
        second["previous_hash"],
    )

    return [first, second]


def test_valid_ledger(monkeypatch):
    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": sample_assets()},
    )

    result = blockchain_ledger.verify_ledger()

    assert result["ledger_valid"] is True
    assert result["records_checked"] == 2


def test_detects_asset_tampering(monkeypatch):
    assets = sample_assets()
    assets[0]["owner_id"] = "ATTACKER"

    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": assets},
    )

    result = blockchain_ledger.verify_ledger()

    assert result["ledger_valid"] is False
    assert result["status"] == "ASSET TAMPERING DETECTED"


def test_detects_broken_hash_chain(monkeypatch):
    assets = sample_assets()
    assets[1]["previous_hash"] = "FAKE-HASH"

    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": assets},
    )

    result = blockchain_ledger.verify_ledger()

    assert result["ledger_valid"] is False
    assert result["status"] == "BROKEN HASH CHAIN"