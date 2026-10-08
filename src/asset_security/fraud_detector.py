from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "marketplace_fraud.log"


def write_fraud_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def analyze_transaction(transaction):
    risk_score = 0
    reasons = []

    amount = float(transaction["amount"])
    transactions_last_minute = int(
        transaction["transactions_last_minute"]
    )
    account_age_days = int(
        transaction["account_age_days"]
    )
    different_country = bool(
        transaction["different_country"]
    )
    asset_value = float(
        transaction["asset_value"]
    )

    if amount >= 5000:
        risk_score += 30
        reasons.append("Unusually high transaction amount")

    if transactions_last_minute >= 8:
        risk_score += 30
        reasons.append("Abnormally high transaction frequency")

    if account_age_days <= 2 and amount >= 1000:
        risk_score += 20
        reasons.append(
            "High-value transaction from a new account"
        )

    if different_country:
        risk_score += 10
        reasons.append(
            "Unusual geographic transaction pattern"
        )

    if asset_value > 0 and amount < asset_value * 0.10:
        risk_score += 20
        reasons.append(
            "Possible virtual economy price manipulation"
        )

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = "HIGH"
        decision = "BLOCKED"

    elif risk_score >= 30:
        risk_level = "MEDIUM"
        decision = "REVIEW REQUIRED"

    else:
        risk_level = "LOW"
        decision = "APPROVED"

    result = {
        "transaction_id": transaction["transaction_id"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "reasons": reasons
    }

    write_fraud_log(
        f"TRANSACTION={transaction['transaction_id']} | "
        f"RISK={risk_score} | "
        f"LEVEL={risk_level} | "
        f"DECISION={decision} | "
        f"REASONS={'; '.join(reasons) if reasons else 'None'}"
    )

    return result


if __name__ == "__main__":

    suspicious_transaction = {
        "transaction_id": "TX-90001",
        "amount": 7500,
        "transactions_last_minute": 12,
        "account_age_days": 1,
        "different_country": True,
        "asset_value": 8000
    }

    result = analyze_transaction(
        suspicious_transaction
    )

    print("=" * 60)
    print("GameShield AI - Marketplace Fraud Detection")
    print("=" * 60)

    print(
        f"\nTransaction ID: "
        f"{result['transaction_id']}"
    )

    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Decision: {result['decision']}")

    print("\nDetection Reasons:")

    if result["reasons"]:
        for reason in result["reasons"]:
            print(f"- {reason}")
    else:
        print("- No suspicious indicators detected")