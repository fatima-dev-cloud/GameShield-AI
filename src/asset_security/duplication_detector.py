from asset_security.asset_registry import load_database, write_log


def detect_duplicate_assets():
    database = load_database()

    seen_hashes = set()
    seen_asset_ids = set()

    duplicates = []

    for asset in database["assets"]:

        asset_id = asset["asset_id"]
        asset_hash = asset["asset_hash"]

        reasons = []

        if asset_id in seen_asset_ids:
            reasons.append("DUPLICATE ASSET ID")

        if asset_hash in seen_hashes:
            reasons.append("DUPLICATE ASSET HASH")

        if reasons:
            duplicates.append({
                "asset_id": asset_id,
                "asset_name": asset["asset_name"],
                "reasons": reasons
            })

        seen_asset_ids.add(asset_id)
        seen_hashes.add(asset_hash)

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