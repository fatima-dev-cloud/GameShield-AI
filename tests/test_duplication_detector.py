from pathlib import Path

import pytest

from asset_security import asset_registry
from asset_security import duplication_detector



@pytest.fixture
def run_scan(tmp_path, monkeypatch):
    log_file = tmp_path / "logs" / "asset_security.log"
    assert isinstance(log_file, Path)
    log_file.resolve().relative_to(tmp_path.resolve())
    monkeypatch.setattr(asset_registry, "LOG_FILE", log_file)

    def run(database):
        def load_database():
            if isinstance(database, BaseException):
                raise database
            return database

        monkeypatch.setattr(
            duplication_detector,
            "load_database",
            load_database,
        )
        return duplication_detector.detect_duplicate_assets()

    return run



def test_detects_duplicate_asset_id(run_scan):
    result = run_scan({
        "assets": [
            {
                "asset_id": "ASSET-001",
                "asset_name": "Synthetic Sword",
                "asset_hash": "hash-one",
            },
            {
                "asset_id": "ASSET-001",
                "asset_name": "Synthetic Shield",
                "asset_hash": "hash-two",
            },
        ]
    })

    assert result == {
        "status": "DUPLICATION EXPLOIT DETECTED",
        "duplicate_count": 1,
        "duplicates": [
            {
                "asset_id": "ASSET-001",
                "asset_name": "Synthetic Shield",
                "reasons": ["DUPLICATE ASSET ID"],
            }
        ],
    }



def test_detects_duplicate_asset_hash(run_scan):
    result = run_scan({
        "assets": [
            {
                "asset_id": "ASSET-001",
                "asset_name": "Synthetic Sword",
                "asset_hash": "shared-hash",
            },
            {
                "asset_id": "ASSET-002",
                "asset_name": "Synthetic Copy",
                "asset_hash": "shared-hash",
            },
        ]
    })

    assert result == {
        "status": "DUPLICATION EXPLOIT DETECTED",
        "duplicate_count": 1,
        "duplicates": [
            {
                "asset_id": "ASSET-002",
                "asset_name": "Synthetic Copy",
                "reasons": ["DUPLICATE ASSET HASH"],
            }
        ],
    }



def test_detects_duplicate_nft_token_id(run_scan):
    result = run_scan({
        "assets": [
            {
                "asset_id": "ASSET-NFT-001",
                "asset_name": "Synthetic NFT One",
                "asset_hash": "nft-hash-one",
                "token_id": "TOKEN-001",
            },
            {
                "asset_id": "ASSET-NFT-002",
                "asset_name": "Synthetic NFT Copy",
                "asset_hash": "nft-hash-two",
                "token_id": "TOKEN-001",
            },
        ]
    })

    assert result == {
        "status": "DUPLICATION EXPLOIT DETECTED",
        "duplicate_count": 1,
        "duplicates": [
            {
                "asset_id": "ASSET-NFT-002",
                "asset_name": "Synthetic NFT Copy",
                "reasons": ["DUPLICATE NFT TOKEN ID"],
            }
        ],
    }


def test_accepts_legitimate_distinct_assets(run_scan):
    result = run_scan({
        "assets": [
            {
                "asset_id": "ASSET-001",
                "asset_name": "Synthetic Sword",
                "asset_hash": "hash-one",
            },
            {
                "asset_id": "ASSET-002",
                "asset_name": "Synthetic Shield",
                "asset_hash": "hash-two",
            },
        ]
    })

    assert result == {
        "status": "NO DUPLICATION DETECTED",
        "duplicate_count": 0,
        "duplicates": [],
    }



@pytest.mark.parametrize(
    "database",
    [
        None,
        [],
        {},
        {"assets": {}},
        asset_registry.AssetDataError("Malformed JSON"),
    ],
)
def test_rejects_malformed_database(run_scan, database):
    result = run_scan(database)

    assert result == {
        "status": "INVALID ASSET DATABASE",
        "duplicate_count": 0,
        "duplicates": [],
    }



@pytest.mark.parametrize(
    "asset",
    [
        None,
        {},
        {
            "asset_id": "ASSET-001",
            "asset_name": "Missing Hash",
        },
        {
            "asset_id": [],
            "asset_name": "Unhashable ID",
            "asset_hash": "hash-one",
        },
        {
            "asset_id": "ASSET-001",
            "asset_name": "Unhashable Hash",
            "asset_hash": [],
        },
        {
            "asset_id": "ASSET-NFT-001",
            "asset_name": "Unhashable Token",
            "asset_hash": "nft-hash-one",
            "token_id": [],
        },
        {
            "asset_id": "ASSET-NFT-002",
            "asset_name": "Numeric Token",
            "asset_hash": "nft-hash-two",
            "token_id": 42,
        },
        {
            "asset_id": "ASSET-NFT-003",
            "asset_name": "Whitespace Token",
            "asset_hash": "nft-hash-three",
            "token_id": "   ",
        },
    ],
)
def test_rejects_malformed_asset_record(run_scan, asset):
    result = run_scan({"assets": [asset]})

    assert result == {
        "status": "INVALID ASSET RECORD",
        "duplicate_count": 0,
        "duplicates": [],
        "failed_record": 1,
    }
