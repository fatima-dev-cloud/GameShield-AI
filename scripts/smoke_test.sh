#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_URL="http://127.0.0.1:5000"
TMP_DIR="$(mktemp -d)"
SERVER_PID=""
FAILURES=0
REQUESTS_IN_WINDOW=0
KERNEL_TOKEN="gameshield-smoke-test-token"

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    PYTHON="$ROOT_DIR/.venv/bin/python"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    PYTHON="$(command -v python3)"
fi

cleanup() {
    local exit_status=$?
    trap - EXIT INT TERM

    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        for _ in {1..50}; do
            kill -0 "$SERVER_PID" 2>/dev/null || break
            sleep 0.1
        done
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            kill -KILL "$SERVER_PID" 2>/dev/null || true
        fi
        wait "$SERVER_PID" 2>/dev/null || true
    fi

    rm -rf -- "$TMP_DIR"
    exit "$exit_status"
}
trap cleanup EXIT INT TERM

pass() {
    printf 'PASS: %s\n' "$1"
}

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    FAILURES=$((FAILURES + 1))
}

# The application permits 10 requests per 10 seconds and blocks the client on
# request 11. Keep each batch below that threshold so the smoke test exercises
# application behavior rather than the rate-limit demonstration.
throttle() {
    if (( REQUESTS_IN_WINDOW >= 9 )); then
        sleep 11
        REQUESTS_IN_WINDOW=0
    fi
}

check_http() {
    local name=$1
    local method=$2
    local path=$3
    local expected_status=$4
    local expected_text=$5
    local body=${6-}
    local authorization=${7-}
    local output_file="$TMP_DIR/response"
    local status

    throttle
    REQUESTS_IN_WINDOW=$((REQUESTS_IN_WINDOW + 1))

    local -a args=(
        --silent --show-error
        --output "$output_file"
        --write-out '%{http_code}'
        --request "$method"
        --max-time 15
    )
    if [[ -n "$body" ]]; then
        args+=(--header 'Content-Type: application/json' --data "$body")
    fi
    if [[ -n "$authorization" ]]; then
        args+=(--header "Authorization: Bearer $authorization")
    fi

    if ! status="$(curl "${args[@]}" "$BASE_URL$path")"; then
        fail "$name (request failed)"
        return
    fi

    if [[ "$status" == "$expected_status" ]] \
        && grep -Fq -- "$expected_text" "$output_file"; then
        pass "$name"
    else
        fail "$name (HTTP $status; expected $expected_status and '$expected_text')"
    fi
}

cd "$ROOT_DIR"

if [[ ! -f models/anti_cheat_model.joblib \
      || ! -f models/content_moderation_model.joblib ]]; then
    fail "trained models are present (run the README training commands first)"
    exit 1
fi

# README section 13 documents this development launch command. Environment
# settings only enable the separately documented educational simulation route.
KERNEL_SIMULATION_ENABLED=true \
KERNEL_SIMULATION_API_TOKEN="$KERNEL_TOKEN" \
VOSK_MODEL_PATH="$ROOT_DIR/models/vosk" \
    "$PYTHON" src/app.py >"$TMP_DIR/server.log" 2>&1 &
SERVER_PID=$!

healthy=false
for _ in {1..50}; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        break
    fi
    if curl --silent --fail --max-time 1 "$BASE_URL/api/status" \
        >"$TMP_DIR/health" 2>/dev/null \
        && grep -Fq '"status":"online"' "$TMP_DIR/health"; then
        healthy=true
        REQUESTS_IN_WINDOW=1
        break
    fi
    sleep 0.2
done

if [[ "$healthy" == true ]]; then
    pass "server becomes healthy"
else
    fail "server becomes healthy"
    sed -n '1,120p' "$TMP_DIR/server.log" >&2 || true
    exit 1
fi

check_http "home page" GET / 200 "GameShield AI"
check_http "dashboard" GET /dashboard 200 "GameShield AI Dashboard"
check_http "dashboard stylesheet" GET /static/dashboard.css 200 "body"
check_http "status API" GET /api/status 200 '"status":"online"'

check_http "anti-cheat analysis" POST /api/anti-cheat/analyze 200 '"module":"AI Anti-Cheat"' \
    '{"accuracy":0.48,"headshot_rate":0.22,"reaction_time":280,"kills_per_minute":1.5,"impossible_actions":0,"tracking_score":0.3}'
check_http "account-sharing analysis" POST /api/anti-cheat/account-sharing 200 '"module":"Account Sharing Detection"' \
    '{"distance_km":10,"time_difference_minutes":120,"device_changed":false,"behavior_change_score":0.1}'
check_http "rank-boosting analysis" POST /api/anti-cheat/rank-boosting 200 '"module":"Rank Boosting Detection"' \
    '{"previous_win_rate":0.5,"current_win_rate":0.55,"rank_increase":1,"matches_played":20,"performance_change_score":0.1}'
check_http "cheat-type analysis" POST /api/anti-cheat/cheat-types 200 '"module":"Cheating Category Detection"' \
    '{"accuracy":0.48,"headshot_rate":0.22,"reaction_time":280,"impossible_actions":0,"hidden_enemy_tracking_events":0,"repetitive_input_score":0.2}'
check_http "kernel-event simulation" POST /api/anti-cheat/kernel-simulation/analyze 200 '"simulation":true' \
    '{"schema_version":"1.0","event_id":"smoke-001","event_type":"PROCESS_START","timestamp":"2026-11-03T00:00:00Z","process_identifier":"smoke-game-client","occurrence_count":1,"simulated_source":"demo_api","simulation":true}' \
    "$KERNEL_TOKEN"

ASSET_NAME="Smoke Asset $SERVER_PID"
check_http "asset registration" POST /api/assets/register 200 '"status":"ASSET REGISTERED"' \
    "{\"asset_name\":\"$ASSET_NAME\",\"owner_id\":\"smoke-owner\",\"asset_type\":\"skin\",\"value\":10}"
ASSET_ID="$($PYTHON - "$TMP_DIR/response" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as response:
    print(json.load(response)["asset"]["asset_id"])
PY
)"
check_http "asset ownership verification" POST /api/assets/verify 200 'OWNERSHIP VERIFIED' \
    "{\"asset_id\":\"$ASSET_ID\",\"owner_id\":\"smoke-owner\"}"
check_http "asset duplication scan" GET /api/assets/duplication-scan 200 '"module":"Duplication Exploit Detection"'
check_http "asset ledger verification" GET /api/assets/blockchain-ledger 200 '"module":"Blockchain-Style Asset Ledger"'
check_http "marketplace analysis" POST /api/marketplace/analyze 200 '"module":"Marketplace Fraud Detection"' \
    '{"transaction_id":"smoke-tx","amount":25,"transactions_last_minute":1,"account_age_days":100,"different_country":false,"asset_value":25}'

USERNAME="smoke-user-$SERVER_PID"
PASSWORD="Smoke-Test-Password-123!"
check_http "identity registration" POST /api/identity/register 201 '"status":"REGISTRATION SUCCESSFUL"' \
    "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\",\"avatar_name\":\"Smoke Avatar\"}"
check_http "identity login" POST /api/identity/login 200 '"status":"AUTHENTICATION SUCCESSFUL"' \
    "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}"
check_http "motion privacy consent" POST /api/identity/privacy 200 '"status":"PRIVACY SETTING UPDATED"' \
    '{"user_id":"smoke-biometric-user","data_type":"motion_tracking","allowed":true}'
check_http "eye privacy consent" POST /api/identity/privacy 200 '"status":"PRIVACY SETTING UPDATED"' \
    '{"user_id":"smoke-biometric-user","data_type":"eye_tracking","allowed":true}'
check_http "biometric protection" POST /api/identity/biometric/protect 200 '"module":"VR/AR Biometric Protection"' \
    '{"user_id":"smoke-biometric-user","biometric_data":{"motion_pattern":[0.1,0.2],"eye_tracking":{"x":0.4,"y":0.6}}}'

check_http "game-action validation" POST /api/infrastructure/validate-action 200 '"status":"ACTION ACCEPTED"' \
    '{"player_id":"smoke-player","movement_speed":5,"damage":50,"fire_rate":3}'
PACKET='{"player_id":"smoke-player","action":"purchase_item","item_id":"DRAGON-SWORD","price":2500}'
SIGNATURE="$($PYTHON - <<'PY'
import sys
sys.path.insert(0, "src")
from infrastructure_security.secure_netcode import sign_packet
print(sign_packet({"player_id": "smoke-player", "action": "purchase_item", "item_id": "DRAGON-SWORD", "price": 2500}))
PY
)"
check_http "secure packet verification" POST /api/infrastructure/verify-packet 200 '"valid":true' \
    "{\"packet\":$PACKET,\"signature\":\"$SIGNATURE\"}"
check_http "threat response" POST /api/infrastructure/threat-response 200 '"module":"Automated Threat Response"' \
    '{"threat_type":"suspicious_login","severity":"LOW","source":"smoke-test"}'

check_http "text moderation" POST /api/moderation/text 200 '"module":"AI Content Moderation"' \
    '{"message":"Good game everyone"}'
check_http "child-safety check" POST /api/moderation/child-safety 200 '"module":"Child Safety"' \
    '{"user_age":13,"content_rating":"E"}'
check_http "real-time moderation" POST /api/moderation/realtime 200 '"module":"Real-Time Multiplayer Moderation"' \
    '{"player_id":"smoke-player","message":"Good game","channel":"team"}'
# A missing upload is the documented validation path and avoids requiring an
# external speech fixture; reaching it proves that the primary voice route is up.
check_http "voice moderation validation" POST /api/moderation/voice 400 '"error":"A WAV file is required in the audio field."'
check_http "DevSecOps report" GET /api/devsecops/report 200 '"overall_status"'

if (( FAILURES > 0 )); then
    printf '\nSmoke test failed: %d check(s) failed.\n' "$FAILURES" >&2
    exit 1
fi

printf '\nSmoke test passed: all primary GameShield AI checks succeeded.\n'
