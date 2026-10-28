from asset_security.asset_registry import (
    AssetDataError,
    load_database,
    write_log,
)


def detect_duplicate_assets():
    try:
        database = load_database()
    except AssetDataError:
        return {
            "status": "INVALID ASSET DATABASE",
            "duplicate_count": 0,
            "duplicates": [],
        }

    if (
        not isinstance(database, dict)
        or not isinstance(database.get("assets"), list)
    ):
        return {
            "status": "INVALID ASSET DATABASE",
            "duplicate_count": 0,
            "duplicates": [],
        }

    seen_hashes = set()
    seen_asset_ids = set()
    seen_token_ids = set()

    duplicates = []

    for index, asset in enumerate(database["assets"]):
        required_fields = (
            "asset_id",
            "asset_hash",
            "asset_name",
        )
        if not isinstance(asset, dict) or any(
            field not in asset for field in required_fields
        ):
            return {
                "status": "INVALID ASSET RECORD",
                "duplicate_count": 0,
                "duplicates": [],
                "failed_record": index + 1,
            }

        asset_id = asset["asset_id"]
        asset_hash = asset["asset_hash"]
        has_token_id = "token_id" in asset
        token_id = asset.get("token_id")

        reasons = []

        try:
            if asset_id in seen_asset_ids:
                reasons.append("DUPLICATE ASSET ID")

            if asset_hash in seen_hashes:
                reasons.append("DUPLICATE ASSET HASH")

            if has_token_id:
                if (
                    not isinstance(token_id, str)
                    or not token_id.strip()
                ):
                    raise TypeError

                if token_id in seen_token_ids:
                    reasons.append("DUPLICATE NFT TOKEN ID")

            seen_asset_ids.add(asset_id)
            seen_hashes.add(asset_hash)
            if has_token_id:
                seen_token_ids.add(token_id)
        except TypeError:
            return {
                "status": "INVALID ASSET RECORD",
                "duplicate_count": 0,
                "duplicates": [],
                "failed_record": index + 1,
            }

        if reasons:
            duplicates.append({
                "asset_id": asset_id,
                "asset_name": asset["asset_name"],
                "reasons": reasons
            })

    if duplicates:
        status = "DUPLICATION EXPLOIT DETECTED"

        write_log(
            f"DUPLICATION_SCAN | "
            f"status={status} | "
            f"duplicates={len(duplicates)}"
        )

    else:
        status = "NO DUPLICATION DETECTED"

        write_log(
            f"DUPLICATION_SCAN | status={status}"
        )

    return {
        "status": status,
        "duplicate_count": len(duplicates),
        "duplicates": duplicates
    }


if __name__ == "__main__":

    print("=" * 60)
    print("GameShield AI - Duplication Exploit Scanner")
    print("=" * 60)

    result = detect_duplicate_assets()

    print(f"\nStatus: {result['status']}")
    print(
        f"Duplicate Assets Found: "
        f"{result['duplicate_count']}"
    )

    if result["duplicates"]:
        print("\nSuspicious assets:")

        for asset in result["duplicates"]:
            print(
                f"- {asset['asset_id']} | "
                f"{', '.join(asset['reasons'])}"
            )