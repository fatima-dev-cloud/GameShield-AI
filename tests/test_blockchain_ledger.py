
import sys
from pathlib import Path

import pytest

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


def sample_versioned_assets():
    from asset_security.asset_registry import calculate_asset_hash

    first = {
        "asset_id": "ASSET-V2-001",
        "asset_name": "Synthetic Sword",
        "asset_type": "virtual_item",
        "owner_id": "PLAYER-V2-001",
        "value": 125.0,
        "created_at": "2026-01-03T00:00:00+00:00",
        "previous_hash": "GENESIS",
        "record_version": 2,
    }
    first["asset_hash"] = calculate_asset_hash(first)

    second = {
        "asset_id": "ASSET-V2-002",
        "asset_name": "Synthetic Shield",
        "asset_type": "collectible",
        "owner_id": "PLAYER-V2-002",
        "value": 250.0,
        "created_at": "2026-01-04T00:00:00+00:00",
        "previous_hash": first["asset_hash"],
        "record_version": 2,
    }
    second["asset_hash"] = calculate_asset_hash(second)

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

def test_valid_versioned_ledger(monkeypatch):
    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": sample_versioned_assets()},
    )

    result = blockchain_ledger.verify_ledger()

    assert result["ledger_valid"] is True
    assert result["records_checked"] == 2
    assert result["ledger_type"] == (
        "LOCAL HASH-LINKED SIMULATION"
    )


def test_detects_versioned_asset_tampering(monkeypatch):
    assets = sample_versioned_assets()
    assets[0]["asset_type"] = "tampered_type"
    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": assets},
    )

    result = blockchain_ledger.verify_ledger()

    assert result["ledger_valid"] is False
    assert result["status"] == "ASSET TAMPERING DETECTED"


def test_rejects_unsupported_record_version(monkeypatch):
    assets = sample_versioned_assets()
    assets[0]["record_version"] = 99
    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": assets},
    )

    result = blockchain_ledger.verify_ledger()

    assert result == {
        "ledger_valid": False,
        "records_checked": 0,
        "status": "INVALID ASSET RECORD",
        "failed_record": 1,
    }


def test_rejects_malformed_record(monkeypatch):
    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": [{"asset_id": "INCOMPLETE"}]},
    )

    result = blockchain_ledger.verify_ledger()

    assert result == {
        "ledger_valid": False,
        "records_checked": 0,
        "status": "INVALID ASSET RECORD",
        "failed_record": 1,
    }


@pytest.mark.parametrize("stored_hash", [None, ""])
def test_rejects_missing_or_empty_hash(
    monkeypatch,
    stored_hash,
):
    asset = sample_versioned_assets()[0]
    if stored_hash is None:
        del asset["asset_hash"]
    else:
        asset["asset_hash"] = stored_hash

    monkeypatch.setattr(
        blockchain_ledger,
        "load_database",
        lambda: {"assets": [asset]},
    )

    result = blockchain_ledger.verify_ledger()

    assert result == {
        "ledger_valid": False,
        "records_checked": 0,
        "status": "INVALID ASSET RECORD",
        "failed_record": 1,
    }
