import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parents[2]

ASSET_FILE = BASE_DIR / "data" / "virtual_assets.json"
LOG_FILE = BASE_DIR / "logs" / "asset_security.log"


def load_database():
    if not ASSET_FILE.exists():
        return {"assets": []}

    with open(ASSET_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_database(database):
    ASSET_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(ASSET_FILE, "w", encoding="utf-8") as file:
        json.dump(database, file, indent=4)


def create_asset_hash(
    asset_id,
    asset_name,
    owner_id,
    timestamp,
    previous_hash
):
    asset_information = (
        f"{asset_id}|"
        f"{asset_name}|"
        f"{owner_id}|"
        f"{timestamp}|"
        f"{previous_hash}"
    )

    return hashlib.sha256(
        asset_information.encode("utf-8")
    ).hexdigest()


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def register_asset(asset_name, owner_id, asset_type, value):
    database = load_database()

    if database["assets"]:
        previous_hash = database["assets"][-1]["asset_hash"]
    else:
        previous_hash = "GENESIS"

    asset_id = "ASSET-" + uuid4().hex[:10].upper()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    asset_hash = create_asset_hash(
        asset_id,
        asset_name,
        owner_id,
        timestamp,
        previous_hash
    )

    asset = {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "asset_type": asset_type,
        "owner_id": owner_id,
        "value": float(value),
        "created_at": timestamp,
        "previous_hash": previous_hash,
        "asset_hash": asset_hash
    }

    database["assets"].append(asset)
    save_database(database)

    write_log(
        f"ASSET_REGISTERED | "
        f"asset_id={asset_id} | "
        f"owner={owner_id} | "
        f"hash={asset_hash}"
    )

    return asset


def verify_asset(asset_id, claimed_owner):
    database = load_database()

    for asset in database["assets"]:
        if asset["asset_id"] == asset_id:

            expected_hash = create_asset_hash(
                asset["asset_id"],
                asset["asset_name"],
                asset["owner_id"],
                asset["created_at"],
                asset["previous_hash"]
            )

            hash_valid = expected_hash == asset["asset_hash"]
            owner_valid = asset["owner_id"] == claimed_owner

            if hash_valid and owner_valid:
                status = "OWNERSHIP VERIFIED"
            elif not hash_valid:
                status = "ASSET TAMPERING DETECTED"
            else:
                status = "OWNERSHIP REJECTED"

            result = {
                "asset_id": asset_id,
                "claimed_owner": claimed_owner,
                "registered_owner": asset["owner_id"],
                "hash_valid": hash_valid,
                "owner_valid": owner_valid,
                "status": status
            }

            write_log(
                f"OWNERSHIP_CHECK | "
                f"asset_id={asset_id} | "
                f"status={status}"
            )

            return result

    return {
        "asset_id": asset_id,
        "status": "ASSET NOT FOUND"
    }


if __name__ == "__main__":

    print("=" * 60)
    print("GameShield AI - Virtual Asset Registry")
    print("=" * 60)

    asset = register_asset(
        asset_name="Dragon Sword",
        owner_id="PLAYER-1001",
        asset_type="Legendary Weapon",
        value=2500
    )

    print("\nVirtual asset registered successfully")
    print("-" * 60)
    print(f"Asset ID: {asset['asset_id']}")
    print(f"Asset Name: {asset['asset_name']}")
    print(f"Owner: {asset['owner_id']}")
    print(f"Asset Type: {asset['asset_type']}")
    print(f"Value: {asset['value']}")
    print(f"SHA-256 Hash: {asset['asset_hash']}")

    print("\nOwnership Verification")
    print("-" * 60)

    result = verify_asset(
        asset["asset_id"],
        "PLAYER-1001"
    )

    print(f"Status: {result['status']}")
    print(f"Hash Valid: {result['hash_valid']}")
    print(f"Owner Valid: {result['owner_valid']}")