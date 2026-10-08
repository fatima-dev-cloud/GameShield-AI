from flask import Flask, jsonify, request

from anti_cheat.detector import analyze_player

from asset_security.asset_registry import (
    register_asset,
    verify_asset
)

from asset_security.fraud_detector import (
    analyze_transaction
)

from asset_security.duplication_detector import (
    detect_duplicate_assets
)

from identity_security.authentication import (
    register_user,
    authenticate_user
)

from identity_security.biometric_protection import (
    encrypt_biometric_data
)

from identity_security.privacy_controls import (
    create_privacy_profile,
    update_privacy_setting,
    check_data_access
)

from infrastructure_security.rate_limiter import (
    check_rate_limit
)

from infrastructure_security.secure_netcode import (
    verify_packet
)

from infrastructure_security.threat_response import (
    respond_to_threat
)

from infrastructure_security.server_validation import (
    validate_game_action
)

from content_moderation.moderator import (
    moderate_text
)

from content_moderation.child_safety import (
    check_age_appropriate_content
)

from content_moderation.realtime_moderation import (
    moderate_multiplayer_message
)

app = Flask(__name__)

@app.before_request
def infrastructure_rate_limit():
    if request.endpoint == "static":
        return None

    client_id = request.remote_addr or "UNKNOWN"

    result = check_rate_limit(client_id)

    if not result["allowed"]:
        return jsonify({
            "platform": "GameShield AI",
            "module": "DDoS Protection",
            "error": result
        }), 429

    return None

@app.route("/")
def home():
    return """
    <h1>GameShield AI</h1>
    <h2>Advanced Gaming & VR/AR Security Platform</h2>
    <p>Status: Security Platform Online</p>

    <h3>Security Modules</h3>
    <ul>
        <li>AI-Powered Anti-Cheat - ACTIVE</li>
        <li>Virtual Asset Protection - ACTIVE</li>
        <li>Metaverse Identity Security - ACTIVE</li>
        <li>Content Moderation - ACTIVE</li>
        <li>Gaming Infrastructure Security - ACTIVE</li>
        <li>DevSecOps Security - ACTIVE</li>
    </ul>
    """


@app.route("/api/status")
def status():
    return jsonify({
        "platform": "GameShield AI",
        "status": "online",
        "modules": {
            "anti_cheat": "active",
            "asset_security": "active",
            "identity_security": "active",
            "content_moderation": "active",
            "infrastructure_security": "active",
            "devsecops": "active",
        },
    })


@app.route("/api/anti-cheat/analyze", methods=["POST"])
def anti_cheat_analysis():
    required_fields = [
        "accuracy",
        "headshot_rate",
        "reaction_time",
        "kills_per_minute",
        "impossible_actions",
        "tracking_score",
    ]

    player_data = request.get_json(silent=True)

    if not isinstance(player_data, dict):
        return jsonify({
            "error": "Request body must contain valid JSON."
        }), 400

    missing_fields = [
        field for field in required_fields
        if field not in player_data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required player data.",
            "missing_fields": missing_fields,
        }), 400

    try:
        clean_player_data = {
            "accuracy": float(player_data["accuracy"]),
            "headshot_rate": float(player_data["headshot_rate"]),
            "reaction_time": float(player_data["reaction_time"]),
            "kills_per_minute": float(player_data["kills_per_minute"]),
            "impossible_actions": float(player_data["impossible_actions"]),
            "tracking_score": float(player_data["tracking_score"]),
        }

        result = analyze_player(clean_player_data)

        return jsonify({
            "platform": "GameShield AI",
            "module": "AI Anti-Cheat",
            "player_behavior": clean_player_data,
            "analysis": result,
        })

    except (TypeError, ValueError):
        return jsonify({
            "error": "All player behavior values must be numeric."
        }), 400

@app.route("/api/assets/register", methods=["POST"])
def api_register_asset():
    data = request.get_json(silent=True)

    required_fields = [
        "asset_name",
        "owner_id",
        "asset_type",
        "value"
    ]

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    missing = [
        field for field in required_fields
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields.",
            "missing_fields": missing
        }), 400

    try:
        asset = register_asset(
            asset_name=str(data["asset_name"]),
            owner_id=str(data["owner_id"]),
            asset_type=str(data["asset_type"]),
            value=float(data["value"])
        )

        return jsonify({
            "platform": "GameShield AI",
            "module": "Virtual Asset Protection",
            "status": "ASSET REGISTERED",
            "asset": asset
        })

    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid asset data."
        }), 400


@app.route("/api/assets/verify", methods=["POST"])
def api_verify_asset():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    if "asset_id" not in data or "owner_id" not in data:
        return jsonify({
            "error": "asset_id and owner_id are required."
        }), 400

    result = verify_asset(
        str(data["asset_id"]),
        str(data["owner_id"])
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "Virtual Asset Protection",
        "verification": result
    })


@app.route("/api/assets/duplication-scan", methods=["GET"])
def api_duplication_scan():
    result = detect_duplicate_assets()

    return jsonify({
        "platform": "GameShield AI",
        "module": "Duplication Exploit Detection",
        "analysis": result
    })


@app.route("/api/marketplace/analyze", methods=["POST"])
def api_marketplace_analysis():
    data = request.get_json(silent=True)

    required_fields = [
        "transaction_id",
        "amount",
        "transactions_last_minute",
        "account_age_days",
        "different_country",
        "asset_value"
    ]

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    missing = [
        field for field in required_fields
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing transaction fields.",
            "missing_fields": missing
        }), 400

    try:
        result = analyze_transaction(data)

        return jsonify({
            "platform": "GameShield AI",
            "module": "Marketplace Fraud Detection",
            "analysis": result
        })

    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid transaction data."
        }), 400

@app.route("/api/identity/register", methods=["POST"])
def api_identity_register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    required_fields = [
        "username",
        "password",
        "avatar_name"
    ]

    missing = [
        field for field in required_fields
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields.",
            "missing_fields": missing
        }), 400

    result = register_user(
        str(data["username"]),
        str(data["password"]),
        str(data["avatar_name"])
    )

    status_code = (
        201
        if result["status"] == "REGISTRATION SUCCESSFUL"
        else 400
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "Metaverse Identity Security",
        "result": result
    }), status_code


@app.route("/api/identity/login", methods=["POST"])
def api_identity_login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    if (
        "username" not in data
        or "password" not in data
    ):
        return jsonify({
            "error": "Username and password required."
        }), 400

    result = authenticate_user(
        str(data["username"]),
        str(data["password"])
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "Secure Authentication",
        "result": result
    })


@app.route(
    "/api/identity/biometric/protect",
    methods=["POST"]
)
def api_protect_biometric():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    if (
        "user_id" not in data
        or "biometric_data" not in data
    ):
        return jsonify({
            "error":
            "user_id and biometric_data required."
        }), 400

    result = encrypt_biometric_data(
        str(data["user_id"]),
        data["biometric_data"]
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "VR/AR Biometric Protection",
        "result": result
    })


@app.route(
    "/api/identity/privacy",
    methods=["POST"]
)
def api_update_privacy():
    data = request.get_json(silent=True)

    required = [
        "user_id",
        "data_type",
        "allowed"
    ]

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    missing = [
        field for field in required
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing privacy fields.",
            "missing_fields": missing
        }), 400

    result = update_privacy_setting(
        str(data["user_id"]),
        str(data["data_type"]),
        bool(data["allowed"])
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "Metaverse Privacy Controls",
        "result": result
    })
 

@app.route(
    "/api/infrastructure/validate-action",
    methods=["POST"]
)
def api_validate_game_action():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    try:
        result = validate_game_action(data)

        return jsonify({
            "platform": "GameShield AI",
            "module": "Server-Side Validation",
            "analysis": result
        })

    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid game action values."
        }), 400


@app.route(
    "/api/infrastructure/verify-packet",
    methods=["POST"]
)
def api_verify_game_packet():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    if (
        "packet" not in data
        or "signature" not in data
    ):
        return jsonify({
            "error":
            "packet and signature are required."
        }), 400

    result = verify_packet(
        data["packet"],
        str(data["signature"])
    )

    status_code = 200 if result["valid"] else 403

    return jsonify({
        "platform": "GameShield AI",
        "module": "Secure Netcode",
        "verification": result
    }), status_code


@app.route(
    "/api/infrastructure/threat-response",
    methods=["POST"]
)
def api_threat_response():
    data = request.get_json(silent=True)

    required = [
        "threat_type",
        "severity",
        "source"
    ]

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    missing = [
        field for field in required
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing threat information.",
            "missing_fields": missing
        }), 400

    result = respond_to_threat(
        str(data["threat_type"]),
        str(data["severity"]),
        str(data["source"])
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "Automated Threat Response",
        "response": result
    })

@app.route(
    "/api/moderation/text",
    methods=["POST"]
)
def api_moderate_text():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    if "message" not in data:
        return jsonify({
            "error": "message is required."
        }), 400

    result = moderate_text(
        str(data["message"])
    )

    return jsonify({
        "platform": "GameShield AI",
        "module": "AI Content Moderation",
        "analysis": result
    })


@app.route(
    "/api/moderation/child-safety",
    methods=["POST"]
)
def api_child_safety():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    if (
        "user_age" not in data
        or "content_rating" not in data
    ):
        return jsonify({
            "error":
            "user_age and content_rating are required."
        }), 400

    try:
        result = check_age_appropriate_content(
            int(data["user_age"]),
            str(data["content_rating"])
        )

        return jsonify({
            "platform": "GameShield AI",
            "module": "Child Safety",
            "analysis": result
        })

    except (TypeError, ValueError):
        return jsonify({
            "error": "user_age must be numeric."
        }), 400


@app.route(
    "/api/moderation/realtime",
    methods=["POST"]
)
def api_realtime_moderation():
    data = request.get_json(silent=True)

    required = [
        "player_id",
        "message",
        "channel"
    ]

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON request required."
        }), 400

    missing = [
        field for field in required
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing moderation fields.",
            "missing_fields": missing
        }), 400

    result = moderate_multiplayer_message(
        str(data["player_id"]),
        str(data["message"]),
        str(data["channel"])
    )

    return jsonify({
        "platform": "GameShield AI",
        "module":
            "Real-Time Multiplayer Moderation",
        "analysis": result
    })
            
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )