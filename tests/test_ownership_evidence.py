from asset_security.ownership_evidence import (
    SIMULATION_LABEL,
    create_simulated_ownership_record,
    hash_off_chain_metadata,
    verify_simulated_ownership,
)


def synthetic_metadata():
    return {
        "asset_id": "ASSET-SYNTHETIC-001",
        "asset_name": "Synthetic Nebula Sword",
        "asset_type": "nft_style_collectible",
        "attributes": {
            "rarity": "legendary",
            "damage": 125,
        },
        "metadata_uri": "local://synthetic/nebula-sword",
    }


def assert_no_persistence(tmp_path):
    assert list(tmp_path.iterdir()) == []


def test_verifies_simulated_ownership(tmp_path):
    assert_no_persistence(tmp_path)
    metadata = synthetic_metadata()
    ownership_record = create_simulated_ownership_record(
        metadata,
        "SYNTHETIC-OWNER-001",
        "TOKEN-SYNTHETIC-001",
    )

    reordered_metadata = {
        "metadata_uri": metadata["metadata_uri"],
        "attributes": metadata["attributes"],
        "asset_type": metadata["asset_type"],
        "asset_name": metadata["asset_name"],
        "asset_id": metadata["asset_id"],
    }
    result = verify_simulated_ownership(
        reordered_metadata,
        ownership_record,
        "SYNTHETIC-OWNER-001",
    )

    assert ownership_record["ledger_type"] == SIMULATION_LABEL
    assert ownership_record["metadata_hash"] == (
        hash_off_chain_metadata(metadata)
    )
    assert result["status"] == "OWNERSHIP VERIFIED"
    assert result["owner_valid"] is True
    assert result["metadata_hash_valid"] is True
    assert result["verified"] is True
    assert "no public blockchain" in result["note"].lower()
    assert_no_persistence(tmp_path)


def test_rejects_incorrect_owner(tmp_path):
    assert_no_persistence(tmp_path)
    metadata = synthetic_metadata()
    ownership_record = create_simulated_ownership_record(
        metadata,
        "SYNTHETIC-OWNER-001",
        "TOKEN-SYNTHETIC-001",
    )

    result = verify_simulated_ownership(
        metadata,
        ownership_record,
        "SYNTHETIC-OWNER-ATTACKER",
    )

    assert result["status"] == "OWNERSHIP REJECTED"
    assert result["owner_valid"] is False
    assert result["metadata_hash_valid"] is True
    assert result["verified"] is False
    assert result["ledger_type"] == SIMULATION_LABEL
    assert_no_persistence(tmp_path)


def test_rejects_tampered_off_chain_metadata(tmp_path):
    assert_no_persistence(tmp_path)
    metadata = synthetic_metadata()
    ownership_record = create_simulated_ownership_record(
        metadata,
        "SYNTHETIC-OWNER-001",
        "TOKEN-SYNTHETIC-001",
    )
    tampered_metadata = synthetic_metadata()
    tampered_metadata["attributes"]["damage"] = 9999

    result = verify_simulated_ownership(
        tampered_metadata,
        ownership_record,
        "SYNTHETIC-OWNER-001",
    )

    assert result["status"] == (
        "OFF-CHAIN METADATA TAMPERING DETECTED"
    )
    assert result["owner_valid"] is True
    assert result["metadata_hash_valid"] is False
    assert result["verified"] is False
    assert result["ledger_type"] == SIMULATION_LABEL
    assert_no_persistence(tmp_path)
