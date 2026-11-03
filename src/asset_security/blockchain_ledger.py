
"""
GameShield AI - Educational Hash-Linked Asset Ledger

Verifies the integrity of existing virtual asset records.

This is a local blockchain-style demonstration.
It is NOT a public blockchain, NFT smart contract,
or decentralized consensus network.
"""

from asset_security.asset_registry import (
    AssetDataError,
    calculate_asset_hash,
    load_database,
)

def verify_ledger():
    database = load_database()
    if not isinstance(database, dict):
        return {
            "ledger_valid": False,
            "records_checked": 0,
            "status": "INVALID LEDGER FORMAT",
        }

    assets = database.get("assets", [])

    if not isinstance(assets, list):
        return {
            "ledger_valid": False,
            "records_checked": 0,
            "status": "INVALID LEDGER FORMAT",
        }

    previous_hash = "GENESIS"

    for index, asset in enumerate(assets):
        required_fields = [
            "asset_id",
            "asset_name",
            "owner_id",
            "created_at",
            "previous_hash",
            "asset_hash",
        ]

        if not isinstance(asset, dict) or any(
            field not in asset for field in required_fields
        ):
            return {
                "ledger_valid": False,
                "records_checked": index,
                "status": "INVALID ASSET RECORD",
                "failed_record": index + 1,
            }

        stored_hash = asset.get("asset_hash")
        if not isinstance(stored_hash, str) or not stored_hash:
            return {
                "ledger_valid": False,
                "records_checked": index,
                "status": "INVALID ASSET RECORD",
                "failed_record": index + 1,
            }

        try:
            expected_hash = calculate_asset_hash(asset)
        except (
            AssetDataError,
            TypeError,
            ValueError,
            OverflowError,
            UnicodeError,
        ):
            return {
                "ledger_valid": False,
                "records_checked": index,
                "status": "INVALID ASSET RECORD",
                "failed_record": index + 1,
            }

        if asset["previous_hash"] != previous_hash:
            return {
                "ledger_valid": False,
                "records_checked": index + 1,
                "status": "BROKEN HASH CHAIN",
                "failed_record": index + 1,
            }

        if stored_hash != expected_hash:
            return {
                "ledger_valid": False,
                "records_checked": index + 1,
                "status": "ASSET TAMPERING DETECTED",
                "failed_record": index + 1,
            }

        previous_hash = stored_hash

    return {
        "ledger_valid": True,
        "records_checked": len(assets),
        "status": "LEDGER INTEGRITY VERIFIED",
        "ledger_type": "LOCAL HASH-LINKED SIMULATION",
        "note": (
            "This verifies local record consistency only. "
            "It does not provide decentralized blockchain "
            "consensus or independently prove ownership."
        ),
    }


if __name__ == "__main__":
    result = verify_ledger()

    print("=" * 55)
    print("GameShield AI - Asset Ledger Verification")
    print("=" * 55)

    print("Status:", result["status"])
    print("Ledger Valid:", result["ledger_valid"])
    print("Records Checked:", result["records_checked"])

    if "failed_record" in result:
        print("Failed Record:", result["failed_record"])

    if "note" in result:
        print("\nNote:", result["note"])