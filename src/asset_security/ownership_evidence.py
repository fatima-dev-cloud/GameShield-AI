"""Local ownership-evidence demonstration for synthetic assets.

This module links off-chain metadata to a simulated ownership record.
It does not connect to or represent a public blockchain.
"""

import hashlib
import json


SIMULATION_LABEL = "LOCAL BLOCKCHAIN SIMULATION"
SIMULATION_DISCLAIMER = (
    "Local demonstration only; no public blockchain, "
    "wallet, smart contract, or decentralized consensus is used."
)


class OwnershipEvidenceError(ValueError):
    """Raised when ownership evidence cannot be created safely."""


def hash_off_chain_metadata(metadata):
    """Return a deterministic SHA-256 hash of off-chain metadata."""
    if not isinstance(metadata, dict) or not metadata:
        raise OwnershipEvidenceError(
            "Off-chain metadata must be a non-empty object."
        )

    try:
        canonical_metadata = json.dumps(
            metadata,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError) as error:
        raise OwnershipEvidenceError(
            "Off-chain metadata is not canonically serializable."
        ) from error

    return hashlib.sha256(
        canonical_metadata.encode("utf-8")
    ).hexdigest()


def create_simulated_ownership_record(
    off_chain_metadata,
    owner_id,
    token_id,
):
    """Create an in-memory record linked to off-chain metadata."""
    if not isinstance(owner_id, str) or not owner_id.strip():
        raise OwnershipEvidenceError(
            "Owner ID must be a non-empty string."
        )
    if not isinstance(token_id, str) or not token_id.strip():
        raise OwnershipEvidenceError(
            "Token ID must be a non-empty string."
        )

    return {
        "ledger_type": SIMULATION_LABEL,
        "token_id": token_id.strip(),
        "owner_id": owner_id.strip(),
        "metadata_hash": hash_off_chain_metadata(
            off_chain_metadata
        ),
        "note": SIMULATION_DISCLAIMER,
    }


def verify_simulated_ownership(
    off_chain_metadata,
    ownership_record,
    claimed_owner,
):
    """Verify owner identity and the off-chain metadata link."""
    required_fields = (
        "ledger_type",
        "token_id",
        "owner_id",
        "metadata_hash",
    )
    if (
        not isinstance(ownership_record, dict)
        or any(
            field not in ownership_record
            for field in required_fields
        )
        or ownership_record.get("ledger_type") != SIMULATION_LABEL
    ):
        return {
            "ledger_type": SIMULATION_LABEL,
            "verified": False,
            "status": "INVALID SIMULATED OWNERSHIP RECORD",
            "note": SIMULATION_DISCLAIMER,
        }

    token_id = ownership_record.get("token_id")
    recorded_owner = ownership_record.get("owner_id")
    stored_metadata_hash = ownership_record.get(
        "metadata_hash"
    )
    if (
        not isinstance(token_id, str)
        or not token_id
        or not isinstance(recorded_owner, str)
        or not recorded_owner
        or not isinstance(stored_metadata_hash, str)
        or not stored_metadata_hash
    ):
        return {
            "ledger_type": SIMULATION_LABEL,
            "verified": False,
            "status": "INVALID SIMULATED OWNERSHIP RECORD",
            "note": SIMULATION_DISCLAIMER,
        }

    try:
        calculated_metadata_hash = hash_off_chain_metadata(
            off_chain_metadata
        )
    except OwnershipEvidenceError:
        return {
            "ledger_type": SIMULATION_LABEL,
            "token_id": token_id,
            "verified": False,
            "status": "INVALID OFF-CHAIN METADATA",
            "note": SIMULATION_DISCLAIMER,
        }

    owner_valid = (
        isinstance(claimed_owner, str)
        and recorded_owner == claimed_owner
    )
    metadata_hash_valid = (
        stored_metadata_hash == calculated_metadata_hash
    )

    if not metadata_hash_valid:
        status = "OFF-CHAIN METADATA TAMPERING DETECTED"
    elif not owner_valid:
        status = "OWNERSHIP REJECTED"
    else:
        status = "OWNERSHIP VERIFIED"

    return {
        "ledger_type": SIMULATION_LABEL,
        "token_id": token_id,
        "claimed_owner": claimed_owner,
        "recorded_owner": recorded_owner,
        "owner_valid": owner_valid,
        "metadata_hash_valid": metadata_hash_valid,
        "verified": owner_valid and metadata_hash_valid,
        "status": status,
        "note": SIMULATION_DISCLAIMER,
    }
