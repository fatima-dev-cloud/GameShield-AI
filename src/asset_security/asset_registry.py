import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parents[2]

ASSET_FILE = BASE_DIR / "data" / "virtual_assets.json"
LOG_FILE = BASE_DIR / "logs" / "asset_security.log"
ASSET_RECORD_VERSION = 2
MAX_ASSET_NAME_LENGTH = 100
MAX_OWNER_ID_LENGTH = 100
MAX_ASSET_TYPE_LENGTH = 100


class AssetDataError(ValueError):
    """Raised when local asset data is invalid or cannot be trusted."""



def load_database():
    if not ASSET_FILE.exists():
        return {"assets": []}

    try:
        with open(ASSET_FILE, "r", encoding="utf-8") as file:
            database = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise AssetDataError(
            "Asset database is unreadable or malformed."
        ) from error

    if not isinstance(database, dict) or not isinstance(
        database.get("assets"), list
    ):
        raise AssetDataError(
            "Asset database must contain an assets list."
        )

    return database


def save_database(database):
    if not isinstance(database, dict) or not isinstance(
        database.get("assets"), list
    ):
        raise AssetDataError(
            "Asset database must contain an assets list."
        )

    ASSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=ASSET_FILE.parent,
            prefix=f".{ASSET_FILE.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(database, file, indent=4, allow_nan=False)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, ASSET_FILE)
    except (OSError, TypeError, ValueError) as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

        raise AssetDataError(
            "Asset database could not be saved safely."
        ) from error


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


def create_versioned_asset_hash(asset):
    if not isinstance(asset, dict):
        raise AssetDataError("Asset record must be an object.")

    required_fields = (
        "asset_id",
        "asset_name",
        "asset_type",
        "owner_id",
        "value",
        "created_at",
        "previous_hash",
        "record_version",
    )
    missing_fields = [
        field for field in required_fields if field not in asset
    ]
    if missing_fields:
        raise AssetDataError("Version 2 asset record is incomplete.")

    record_version = asset["record_version"]
    if (
        type(record_version) is not int
        or record_version != ASSET_RECORD_VERSION
    ):
        raise AssetDataError("Unsupported asset record version.")

    value = asset["value"]
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise AssetDataError("Asset value must be a finite number.")

    canonical_record = {
        "asset_id": asset["asset_id"],
        "asset_name": asset["asset_name"],
        "asset_type": asset["asset_type"],
        "owner_id": asset["owner_id"],
        "value": value,
        "created_at": asset["created_at"],
        "previous_hash": asset["previous_hash"],
        "record_version": record_version,
    }

    canonical_json = json.dumps(
        canonical_record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def calculate_asset_hash(asset):
    if not isinstance(asset, dict):
        raise AssetDataError("Asset record must be an object.")

    if "record_version" not in asset:
        required_fields = (
            "asset_id",
            "asset_name",
            "owner_id",
            "created_at",
            "previous_hash",
        )
        if any(field not in asset for field in required_fields):
            raise AssetDataError("Legacy asset record is incomplete.")

        return create_asset_hash(
            asset["asset_id"],
            asset["asset_name"],
            asset["owner_id"],
            asset["created_at"],
            asset["previous_hash"],
        )

    record_version = asset["record_version"]
    if (
        type(record_version) is int
        and record_version == ASSET_RECORD_VERSION
    ):
        return create_versioned_asset_hash(asset)

    raise AssetDataError("Unsupported asset record version.")


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def register_asset(asset_name, owner_id, asset_type, value):
    if not isinstance(asset_name, str):
        raise AssetDataError("Asset name must be a string.")
    asset_name = asset_name.strip()
    if not asset_name or len(asset_name) > MAX_ASSET_NAME_LENGTH:
        raise AssetDataError("Asset name is empty or too long.")

    if not isinstance(owner_id, str):
        raise AssetDataError("Owner ID must be a string.")
    owner_id = owner_id.strip()
    if not owner_id or len(owner_id) > MAX_OWNER_ID_LENGTH:
        raise AssetDataError("Owner ID is empty or too long.")

    if not isinstance(asset_type, str):
        raise AssetDataError("Asset type must be a string.")
    asset_type = asset_type.strip()
    if not asset_type or len(asset_type) > MAX_ASSET_TYPE_LENGTH:
        raise AssetDataError("Asset type is empty or too long.")

    if isinstance(value, bool):
        raise AssetDataError("Asset value must be a number.")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise AssetDataError("Asset value must be a number.") from error
    if not math.isfinite(value) or value < 0:
        raise AssetDataError(
            "Asset value must be finite and non-negative."
        )

    database = load_database()

    if database["assets"]:
        last_asset = database["assets"][-1]
        if (
            not isinstance(last_asset, dict)
            or not isinstance(last_asset.get("asset_hash"), str)
            or not last_asset["asset_hash"]
        ):
            raise AssetDataError("Last asset record is malformed.")
        previous_hash = last_asset["asset_hash"]
    else:
        previous_hash = "GENESIS"

    asset_id = "ASSET-" + uuid4().hex[:10].upper()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    asset = {
        "record_version": ASSET_RECORD_VERSION,
        "asset_id": asset_id,
        "asset_name": asset_name,
        "asset_type": asset_type,
        "owner_id": owner_id,
        "value": value,
        "created_at": timestamp,
        "previous_hash": previous_hash,
    }

    asset_hash = calculate_asset_hash(asset)
    asset["asset_hash"] = asset_hash

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
    try:
        database = load_database()
    except AssetDataError as error:
        return {
            "asset_id": asset_id,
            "status": "ASSET DATABASE ERROR",
            "error": str(error),
        }

    for index, asset in enumerate(database["assets"]):
        if not isinstance(asset, dict):
            return {
                "asset_id": asset_id,
                "claimed_owner": claimed_owner,
                "status": "INVALID ASSET RECORD",
                "failed_record": index + 1,
            }

        if not asset.get("asset_id") == asset_id:
            continue

        try:
            expected_hash = calculate_asset_hash(asset)
            stored_hash = asset.get("asset_hash")
            if not isinstance(stored_hash, str) or not stored_hash:
                raise AssetDataError(
                    "Asset hash is missing or invalid."
                )
            registered_owner = asset.get("owner_id")
            if not isinstance(registered_owner, str):
                raise AssetDataError(
                    "Asset owner is missing or invalid."
                )
        except (
            AssetDataError,
            TypeError,
            ValueError,
            OverflowError,
            UnicodeError,
        ) as error:
            return {
                "asset_id": asset_id,
                "claimed_owner": claimed_owner,
                "status": "INVALID ASSET RECORD",
                "failed_record": index + 1,
                "error": str(error),
            }

        hash_valid = expected_hash == stored_hash
        owner_valid = registered_owner == claimed_owner

        if hash_valid and owner_valid:
            status = "OWNERSHIP VERIFIED"
        elif not hash_valid:
            status = "ASSET TAMPERING DETECTED"
        else:
            status = "OWNERSHIP REJECTED"

        result = {
            "asset_id": asset_id,
            "claimed_owner": claimed_owner,
            "registered_owner": registered_owner,
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