import math

import pytest

from app import app
from asset_security import asset_registry


@pytest.fixture
def isolated_registry(tmp_path, monkeypatch):
    asset_file = tmp_path / "data" / "virtual_assets.json"
    log_file = tmp_path / "logs" / "asset_security.log"

    monkeypatch.setattr(asset_registry, "ASSET_FILE", asset_file)
    monkeypatch.setattr(asset_registry, "LOG_FILE", log_file)

    temporary_root = tmp_path.resolve()
    for path in (asset_registry.ASSET_FILE, asset_registry.LOG_FILE):
        path.resolve().relative_to(temporary_root)

    return asset_registry


def register_synthetic_asset(registry, value=125.5):
    return registry.register_asset(
        asset_name="Synthetic Sword",
        owner_id="OWNER-SYNTHETIC",
        asset_type="Arbitrary Synthetic Type",
        value=value,
    )


def create_legacy_asset(registry):
    asset = {
        "asset_id": "LEGACY-SYNTHETIC-001",
        "asset_name": "Legacy Synthetic Item",
        "asset_type": "Legacy Arbitrary Type",
        "owner_id": "LEGACY-OWNER",
        "value": 10.0,
        "created_at": "2026-01-01T00:00:00+00:00",
        "previous_hash": "GENESIS",
    }
    asset["asset_hash"] = registry.create_asset_hash(
        asset["asset_id"],
        asset["asset_name"],
        asset["owner_id"],
        asset["created_at"],
        asset["previous_hash"],
    )
    return asset


def test_registers_and_verifies_version_2_asset(isolated_registry):
    asset = register_synthetic_asset(isolated_registry)
    assert asset["record_version"] == 2
    assert asset["asset_hash"] == isolated_registry.calculate_asset_hash(asset)
    result = isolated_registry.verify_asset(asset["asset_id"], asset["owner_id"])
    assert result["status"] == "OWNERSHIP VERIFIED"
    assert result["hash_valid"] is True
    assert result["owner_valid"] is True


def test_verifies_legacy_asset(isolated_registry):
    asset = create_legacy_asset(isolated_registry)
    isolated_registry.save_database({"assets": [asset]})
    result = isolated_registry.verify_asset(asset["asset_id"], asset["owner_id"])
    assert result["status"] == "OWNERSHIP VERIFIED"
    assert result["hash_valid"] is True


def test_rejects_wrong_owner(isolated_registry):
    asset = register_synthetic_asset(isolated_registry)
    result = isolated_registry.verify_asset(asset["asset_id"], "OTHER-OWNER")
    assert result["status"] == "OWNERSHIP REJECTED"
    assert result["hash_valid"] is True
    assert result["owner_valid"] is False


def test_detects_version_2_asset_tampering(isolated_registry):
    asset = register_synthetic_asset(isolated_registry)
    database = isolated_registry.load_database()
    database["assets"][0]["asset_type"] = "Tampered Type"
    isolated_registry.save_database(database)
    result = isolated_registry.verify_asset(asset["asset_id"], asset["owner_id"])
    assert result["status"] == "ASSET TAMPERING DETECTED"
    assert result["hash_valid"] is False


def test_accepts_numeric_string_value(isolated_registry):
    asset = register_synthetic_asset(isolated_registry, value="125.50")
    assert asset["value"] == 125.5
    result = isolated_registry.verify_asset(asset["asset_id"], asset["owner_id"])
    assert result["status"] == "OWNERSHIP VERIFIED"


@pytest.mark.parametrize(
    "invalid_value",
    [True, -1, math.nan, math.inf, -math.inf],
    ids=["boolean", "negative", "nan", "infinity", "negative-infinity"],
)
def test_rejects_invalid_values(isolated_registry, invalid_value):
    with pytest.raises(asset_registry.AssetDataError):
        register_synthetic_asset(isolated_registry, value=invalid_value)


def test_rejects_unsupported_record_version(isolated_registry):
    asset = register_synthetic_asset(isolated_registry)
    database = isolated_registry.load_database()
    database["assets"][0]["record_version"] = 99
    isolated_registry.save_database(database)
    result = isolated_registry.verify_asset(asset["asset_id"], asset["owner_id"])
    assert result["status"] == "INVALID ASSET RECORD"


@pytest.mark.parametrize("hash_value", [None, ""], ids=["missing", "empty"])
def test_rejects_missing_or_empty_hash(isolated_registry, hash_value):
    asset = register_synthetic_asset(isolated_registry)
    database = isolated_registry.load_database()
    if hash_value is None:
        database["assets"][0].pop("asset_hash")
    else:
        database["assets"][0]["asset_hash"] = hash_value
    isolated_registry.save_database(database)
    result = isolated_registry.verify_asset(asset["asset_id"], asset["owner_id"])
    assert result["status"] == "INVALID ASSET RECORD"


@pytest.mark.parametrize(
    "malformed_record",
    [
        None,
        {
            "asset_id": "MALFORMED-SYNTHETIC-001",
            "record_version": 2,
        },
    ],
    ids=["non-object", "incomplete-object"],
)
def test_malformed_records_fail_safely(isolated_registry, malformed_record):
    isolated_registry.save_database({"assets": [malformed_record]})
    result = isolated_registry.verify_asset(
        "MALFORMED-SYNTHETIC-001",
        "SYNTHETIC-OWNER",
    )
    assert result["status"] == "INVALID ASSET RECORD"


@pytest.mark.parametrize("boolean_value", [True, False])
def test_api_rejects_boolean_asset_value(
    isolated_registry,
    boolean_value,
    monkeypatch,
):
    monkeypatch.setitem(app.config, "TESTING", True)

    with app.test_client() as client:
        response = client.post(
            "/api/assets/register",
            json={
                "asset_name": "Synthetic API Item",
                "owner_id": "API-OWNER",
                "asset_type": "Arbitrary API Type",
                "value": boolean_value,
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid asset data."}
    assert not isolated_registry.ASSET_FILE.exists()
