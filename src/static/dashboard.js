
const playerType = document.getElementById("playerType");
const analyzeButton = document.getElementById("analyzeButton");
const resultBox = document.getElementById("result");

const demoPlayers = {
    legit: {
        accuracy: 0.47,
        headshot_rate: 0.21,
        reaction_time: 290,
        kills_per_minute: 1.5,
        impossible_actions: 0,
        tracking_score: 0.39
    },
    cheater: {
        accuracy: 0.98,
        headshot_rate: 0.95,
        reaction_time: 40,
        kills_per_minute: 7.5,
        impossible_actions: 15,
        tracking_score: 0.99
    }
};

analyzeButton.addEventListener("click", async () => {
    analyzeButton.disabled = true;
    resultBox.textContent = "Analyzing player behavior...";

    try {
        const response = await fetch("/api/anti-cheat/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(demoPlayers[playerType.value])
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis failed.");
        }

        const analysis = data.analysis;

        resultBox.textContent =
            "Status: " + analysis.status + "\n" +
            "Risk Level: " + analysis.risk_level + "\n" +
            "Cheat Probability: " +
            analysis.cheat_probability + "%";

    } catch (error) {
        resultBox.textContent = "Error: " + error.message;
    } finally {
        analyzeButton.disabled = false;
    }
});


// Virtual Asset & Marketplace Fraud Detection

const transactionType = document.getElementById("transactionType");
const transactionButton = document.getElementById(
    "analyzeTransactionButton"
);
const transactionResult = document.getElementById(
    "transactionResult"
);

// Synthetic transactions for educational testing
const demoTransactions = {
    normal: {
        transaction_id: "DEMO-NORMAL-001",
        amount: 25,
        transactions_last_minute: 1,
        account_age_days: 365,
        different_country: false,
        asset_value: 25
    },

    suspicious: {
        transaction_id: "DEMO-SUSPICIOUS-001",
        amount: 9500,
        transactions_last_minute: 40,
        account_age_days: 1,
        different_country: true,
        asset_value: 100
    }
};

transactionButton.addEventListener("click", async () => {
    transactionButton.disabled = true;
    transactionResult.textContent =
        "Analyzing marketplace transaction...";

    try {
        const selectedTransaction =
            demoTransactions[transactionType.value];

        const response = await fetch(
            "/api/marketplace/analyze",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(selectedTransaction)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Transaction analysis failed."
            );
        }

        // Show the actual backend analysis, without
        // assuming specific fraud detector response keys.
        transactionResult.textContent =
            "Transaction ID: " +
            selectedTransaction.transaction_id +
            "\n\nBackend Analysis:\n" +
            JSON.stringify(data.analysis, null, 2);

    } catch (error) {
        transactionResult.textContent =
            "Error: " + error.message;
    } finally {
        transactionButton.disabled = false;
    }
});

// ===========================================
// Virtual Asset Registration & Verification
// ===========================================

const registerAssetButton = document.getElementById(
    "registerAssetButton"
);
const verifyAssetButton = document.getElementById(
    "verifyAssetButton"
);
const scanDuplicatesButton = document.getElementById(
    "scanDuplicatesButton"
);

const assetRegisterResult = document.getElementById(
    "assetRegisterResult"
);
const assetVerifyResult = document.getElementById(
    "assetVerifyResult"
);
const duplicationResult = document.getElementById(
    "duplicationResult"
);

async function assetApiRequest(url, method, payload) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (payload !== undefined) {
        options.body = JSON.stringify(payload);
    }

    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || "Request failed."
        );
    }

    return data;
}

// 1. Register Asset

registerAssetButton.addEventListener("click", async () => {
    const name = document.getElementById("assetName").value.trim();
    const owner = document.getElementById("assetOwner").value.trim();
    const type = document.getElementById("assetType").value;
    const valueText = document.getElementById("assetValue").value;
    const value = Number(valueText);

    if (!name || !owner || valueText === "" ||
        !Number.isFinite(value) || value < 0) {
        assetRegisterResult.textContent =
            "Please enter valid asset information.";
        return;
    }

    registerAssetButton.disabled = true;
    assetRegisterResult.textContent = "Registering asset...";

    try {
        const data = await assetApiRequest(
            "/api/assets/register",
            "POST",
            {
                asset_name: name,
                owner_id: owner,
                asset_type: type,
                value: value
            }
        );

        assetRegisterResult.textContent =
            JSON.stringify(data, null, 2);

        // Auto-fill verification fields if the backend
        // returns an asset_id.
        if (data.asset && data.asset.asset_id != null) {
            document.getElementById("verifyAssetId").value =
                String(data.asset.asset_id);
        }

        document.getElementById("verifyOwnerId").value = owner;

    } catch (error) {
        assetRegisterResult.textContent =
            "Error: " + error.message;
    } finally {
        registerAssetButton.disabled = false;
    }
});

// 2. Verify Asset Ownership

verifyAssetButton.addEventListener("click", async () => {
    const assetId = document.getElementById(
        "verifyAssetId"
    ).value.trim();

    const ownerId = document.getElementById(
        "verifyOwnerId"
    ).value.trim();

    if (!assetId || !ownerId) {
        assetVerifyResult.textContent =
            "Please enter Asset ID and Owner ID.";
        return;
    }

    verifyAssetButton.disabled = true;
    assetVerifyResult.textContent = "Verifying ownership...";

    try {
        const data = await assetApiRequest(
            "/api/assets/verify",
            "POST",
            {
                asset_id: assetId,
                owner_id: ownerId
            }
        );

        assetVerifyResult.textContent =
            JSON.stringify(data.verification, null, 2);

    } catch (error) {
        assetVerifyResult.textContent =
            "Error: " + error.message;
    } finally {
        verifyAssetButton.disabled = false;
    }
});

// 3. Scan for Duplicate Assets

scanDuplicatesButton.addEventListener("click", async () => {
    scanDuplicatesButton.disabled = true;
    duplicationResult.textContent =
        "Scanning asset registry...";

    try {
        const data = await assetApiRequest(
            "/api/assets/duplication-scan",
            "GET"
        );

        duplicationResult.textContent =
            JSON.stringify(data.analysis, null, 2);

    } catch (error) {
        duplicationResult.textContent =
            "Error: " + error.message;
    } finally {
        scanDuplicatesButton.disabled = false;
    }
});


// ==========================================
// METAVERSE IDENTITY SECURITY DASHBOARD
// ==========================================

async function identityApiRequest(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error ||
            data.result?.message ||
            "Identity request failed."
        );
    }

    return data;
}

// Hide sensitive fields if returned by backend
function safeIdentityResult(data) {
    const copy = JSON.parse(JSON.stringify(data));

    function redact(obj) {
        if (!obj || typeof obj !== "object") return;

        for (const key of Object.keys(obj)) {
            if (/password|secret|token|encrypted_data|ciphertext|key/i.test(key)) {
                obj[key] = "[REDACTED]";
            } else {
                redact(obj[key]);
            }
        }
    }

    redact(copy);
    return JSON.stringify(copy, null, 2);
}

// 1. Register Demo User

document.getElementById("registerIdentityButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "registerIdentityButton"
        );
        const resultBox = document.getElementById(
            "identityRegisterResult"
        );

        const username = document.getElementById(
            "identityUsername"
        ).value.trim();

        const password = document.getElementById(
            "identityPassword"
        ).value;

        const avatarName = document.getElementById(
            "identityAvatar"
        ).value.trim();

        if (!username || !password || !avatarName) {
            resultBox.textContent =
                "Please fill all registration fields.";
            return;
        }

        button.disabled = true;
        resultBox.textContent = "Registering demo identity...";

        try {
            const data = await identityApiRequest(
                "/api/identity/register",
                {
                    username: username,
                    password: password,
                    avatar_name: avatarName
                }
            );

            resultBox.textContent = safeIdentityResult(data);

            document.getElementById(
                "loginUsername"
            ).value = username;

            document.getElementById(
                "loginPassword"
            ).value = "";

        } catch (error) {
            resultBox.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// 2. Secure Login

document.getElementById("loginIdentityButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "loginIdentityButton"
        );
        const resultBox = document.getElementById(
            "identityLoginResult"
        );

        const username = document.getElementById(
            "loginUsername"
        ).value.trim();

        const password = document.getElementById(
            "loginPassword"
        ).value;

        if (!username || !password) {
            resultBox.textContent =
                "Username and password required.";
            return;
        }

        button.disabled = true;
        resultBox.textContent = "Checking credentials...";

        try {
            const data = await identityApiRequest(
                "/api/identity/login",
                {
                    username: username,
                    password: password
                }
            );

            resultBox.textContent = safeIdentityResult(data);

        } catch (error) {
            resultBox.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// 3. Protect Synthetic Biometric Data

document.getElementById("protectBiometricButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "protectBiometricButton"
        );
        const resultBox = document.getElementById(
            "biometricResult"
        );

        const userId = document.getElementById(
            "biometricUserId"
        ).value.trim();

        if (!userId) {
            resultBox.textContent = "Demo User ID required.";
            return;
        }

        button.disabled = true;
        resultBox.textContent =
            "Protecting synthetic biometric data...";

        try {
            const data = await identityApiRequest(
                "/api/identity/biometric/protect",
                {
                    user_id: userId,
                    biometric_data: {
                        motion_pattern: [0.12, 0.34, 0.56],
                        eye_tracking: {
                            x: 0.45,
                            y: 0.62
                        },
                        source: "synthetic_demo"
                    }
                }
            );

            resultBox.textContent = safeIdentityResult(data);

        } catch (error) {
            resultBox.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// 4. Privacy Controls

document.getElementById("updatePrivacyButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "updatePrivacyButton"
        );
        const resultBox = document.getElementById(
            "privacyResult"
        );

        const userId = document.getElementById(
            "privacyUserId"
        ).value.trim();

        const dataType = document.getElementById(
            "privacyDataType"
        ).value;

        const allowed = document.getElementById(
            "privacyAllowed"
        ).value === "true";

        if (!userId) {
            resultBox.textContent = "Demo User ID required.";
            return;
        }

        button.disabled = true;
        resultBox.textContent =
            "Updating privacy setting...";

        try {
            const data = await identityApiRequest(
                "/api/identity/privacy",
                {
                    user_id: userId,
                    data_type: dataType,
                    allowed: allowed
                }
            );

            resultBox.textContent = safeIdentityResult(data);

        } catch (error) {
            resultBox.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });


// ========================================
// GAMING INFRASTRUCTURE SECURITY
// ========================================

async function infrastructureRequest(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    return {
        httpStatus: response.status,
        data: data
    };
}

function displayInfrastructureResult(element, response) {
    element.textContent =
        "HTTP Status: " + response.httpStatus +
        "\n\n" + JSON.stringify(response.data, null, 2);
}


// 1. Server-Side Validation - FIXED

document.getElementById("validateActionButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "validateActionButton"
        );

        const result = document.getElementById(
            "actionValidationResult"
        );

        const actionType = document.getElementById(
            "gameActionType"
        ).value;

        // Field names match server_validation.py
        const payload = actionType === "normal"
            ? {
                player_id: "demo_player_001",
                movement_speed: 5,
                damage: 50,
                fire_rate: 3
            }
            : {
                player_id: "demo_player_001",
                movement_speed: 80,
                damage: 999,
                fire_rate: 30
            };

        button.disabled = true;
        result.textContent = "Validating game action...";

        try {
            const response = await infrastructureRequest(
                "/api/infrastructure/validate-action",
                payload
            );

            displayInfrastructureResult(result, response);

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

 // 2. Secure Netcode - FIXED

document.getElementById("verifyPacketButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "verifyPacketButton"
        );

        const result = document.getElementById(
            "packetVerificationResult"
        );

        const signature = document.getElementById(
            "packetSignature"
        ).value.trim();

        // Backend expects a dictionary/object,
        // not a plain string.
        const packet = {
            player_id: "demo_player_001",
            action: "purchase_item",
            item_id: "DRAGON-SWORD",
            price: 2500
        };

        button.disabled = true;
        result.textContent = "Verifying packet...";

        try {
            const response = await infrastructureRequest(
                "/api/infrastructure/verify-packet",
                {
                    packet: packet,
                    signature: signature
                }
            );

            displayInfrastructureResult(result, response);

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });


// 3. Automated Threat Response

document.getElementById("threatResponseButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "threatResponseButton"
        );
        const result = document.getElementById(
            "threatResponseResult"
        );

        const threatType = document.getElementById(
            "threatType"
        ).value;

        const severity = document.getElementById(
            "threatSeverity"
        ).value;

        button.disabled = true;
        result.textContent = "Analyzing threat...";

        try {
            const response = await infrastructureRequest(
                "/api/infrastructure/threat-response",
                {
                    threat_type: threatType,
                    severity: severity,
                    source: "synthetic_demo_traffic"
                }
            );

            displayInfrastructureResult(result, response);

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });


// ===========================================
// AI CONTENT MODERATION DASHBOARD
// ===========================================

async function moderationApiRequest(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {
        throw new Error(
            "Server returned a non-JSON response. HTTP " +
            response.status
        );
    }

    const data = await response.json();

    return {
        httpStatus: response.status,
        data: data
    };
}

function showModerationResult(element, response) {
    element.textContent =
        "HTTP Status: " + response.httpStatus +
        "\n\n" + JSON.stringify(response.data, null, 2);
}

// 1. AI Text Moderation

document.getElementById("moderateTextButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "moderateTextButton"
        );

        const result = document.getElementById(
            "moderationTextResult"
        );

        const message = document.getElementById(
            "moderationMessage"
        ).value.trim();

        if (!message) {
            result.textContent = "Please enter a message.";
            return;
        }

        button.disabled = true;
        result.textContent = "Analyzing message...";

        try {
            const response = await moderationApiRequest(
                "/api/moderation/text",
                { message: message }
            );

            showModerationResult(result, response);

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// 2. Child Safety

document.getElementById("checkChildSafetyButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "checkChildSafetyButton"
        );

        const result = document.getElementById(
            "childSafetyResult"
        );

        const age = Number(document.getElementById(
            "childUserAge"
        ).value);

        const rating = document.getElementById(
            "childContentRating"
        ).value;

        if (!Number.isInteger(age) || age < 1 || age > 120) {
            result.textContent = "Enter a valid player age.";
            return;
        }

        button.disabled = true;
        result.textContent = "Checking content access...";

        try {
            const response = await moderationApiRequest(
                "/api/moderation/child-safety",
                {
                    user_age: age,
                    content_rating: rating
                }
            );

            showModerationResult(result, response);

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// 3. Real-Time Multiplayer Moderation

document.getElementById("moderateMultiplayerButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "moderateMultiplayerButton"
        );

        const result = document.getElementById(
            "multiplayerModerationResult"
        );

        const playerId = document.getElementById(
            "multiplayerPlayerId"
        ).value.trim();

        const channel = document.getElementById(
            "multiplayerChannel"
        ).value;

        const message = document.getElementById(
            "multiplayerMessage"
        ).value.trim();

        if (!playerId || !message) {
            result.textContent =
                "Player ID and message are required.";
            return;
        }

        button.disabled = true;
        result.textContent = "Moderating multiplayer chat...";

        try {
            const response = await moderationApiRequest(
                "/api/moderation/realtime",
                {
                    player_id: playerId,
                    message: message,
                    channel: channel
                }
            );

            showModerationResult(result, response);

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// 4. Offline Voice Moderation

document.getElementById("moderateVoiceButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "moderateVoiceButton"
        );

        const result = document.getElementById(
            "voiceModerationResult"
        );

        const audioInput = document.getElementById(
            "voiceAudioFile"
        );

        const audioFile = audioInput.files[0];

        if (!audioFile) {
            result.textContent = "Select a WAV audio sample.";
            return;
        }

        const maximumAudioSize = 10 * 1024 * 1024;

        if (audioFile.size > maximumAudioSize) {
            result.textContent =
                "Audio sample must not exceed 10 MB.";
            return;
        }

        const formData = new FormData();
        formData.append("audio", audioFile);

        button.disabled = true;
        result.textContent =
            "Transcribing and moderating voice...";

        try {
            const response = await fetch(
                "/api/moderation/voice",
                {
                    method: "POST",
                    body: formData
                }
            );

            const contentType =
                response.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {
                throw new Error(
                    "Server returned a non-JSON response. HTTP " +
                    response.status
                );
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Voice moderation failed."
                );
            }

            showModerationResult(
                result,
                {
                    httpStatus: response.status,
                    data: data
                }
            );

        } catch (error) {
            result.textContent = "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });

// ========================================
// DEVSECOPS SECURITY DASHBOARD
// ========================================

document.getElementById("loadDevsecopsReportButton")
    .addEventListener("click", async () => {

        const button = document.getElementById(
            "loadDevsecopsReportButton"
        );

        const result = document.getElementById(
            "devsecopsReportResult"
        );

        button.disabled = true;
        result.textContent = "Loading security report...";

        try {
            const response = await fetch(
                "/api/devsecops/report"
            );

            const contentType =
                response.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {
                throw new Error(
                    "Server returned a non-JSON response."
                );
            }

            const data = await response.json();

            result.textContent =
                "HTTP Status: " + response.status +
                "\n\n" + JSON.stringify(data, null, 2);

        } catch (error) {
            result.textContent =
                "Error: " + error.message;
        } finally {
            button.disabled = false;
        }
    });


/* ==========================================
   Behavioral Anti-Cheat Detection
   ========================================== */

const sharingScenarios = {
    legitimate: {
        distance_km: 10,
        time_difference_minutes: 120,
        device_changed: false,
        behavior_change_score: 0.10
    },
    suspicious: {
        distance_km: 5000,
        time_difference_minutes: 20,
        device_changed: true,
        behavior_change_score: 0.90
    }
};

const boostingScenarios = {
    legitimate: {
        previous_win_rate: 0.45,
        current_win_rate: 0.50,
        rank_increase: 1,
        matches_played: 25,
        performance_change_score: 0.10
    },
    suspicious: {
        previous_win_rate: 0.35,
        current_win_rate: 0.90,
        rank_increase: 7,
        matches_played: 8,
        performance_change_score: 0.85
    }
};

async function runBehavioralAnalysis(url, payload, resultBox) {
    resultBox.textContent = "Analyzing activity...";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis failed.");
        }

        const signals = data.signals.length
            ? data.signals.join(", ")
            : "No suspicious signals";

        resultBox.textContent =
            `Risk Level: ${data.risk_level}\n` +
            `Risk Score: ${data.risk_score}/100\n` +
            `Suspicious: ${data.suspicious ? "Yes" : "No"}\n` +
            `Signals: ${signals}\n\n` +
            `${data.note}`;

        resultBox.style.whiteSpace = "pre-line";

    } catch (error) {
        resultBox.textContent = `Error: ${error.message}`;
    }
}

const sharingButton = document.getElementById(
    "sharingAnalyzeButton"
);

if (sharingButton) {
    sharingButton.addEventListener("click", async () => {
        const scenario = document.getElementById(
            "sharingScenario"
        ).value;

        const resultBox = document.getElementById(
            "sharingResult"
        );

        await runBehavioralAnalysis(
            "/api/anti-cheat/account-sharing",
            sharingScenarios[scenario],
            resultBox
        );
    });
}

const boostingButton = document.getElementById(
    "boostingAnalyzeButton"
);

if (boostingButton) {
    boostingButton.addEventListener("click", async () => {
        const scenario = document.getElementById(
            "boostingScenario"
        ).value;

        const resultBox = document.getElementById(
            "boostingResult"
        );

        await runBehavioralAnalysis(
            "/api/anti-cheat/rank-boosting",
            boostingScenarios[scenario],
            resultBox
        );
    });
}


/* ==========================================
   GameShield AI - Cheating Category Detection
   Educational simulated gameplay scenarios
   ========================================== */

const cheatTypeBasePlayer = {
    accuracy: 0.48,
    headshot_rate: 0.22,
    reaction_time: 280,
    impossible_actions: 0,
    hidden_enemy_tracking_events: 0,
    repetitive_input_score: 0.20
};

const cheatTypeScenarios = {
    legit: cheatTypeBasePlayer,

    aimbot: {
        ...cheatTypeBasePlayer,
        accuracy: 0.98,
        headshot_rate: 0.96,
        reaction_time: 40
    },

    wallhack: {
        ...cheatTypeBasePlayer,
        hidden_enemy_tracking_events: 9
    },

    automation: {
        ...cheatTypeBasePlayer,
        impossible_actions: 12,
        repetitive_input_score: 0.98
    }
};

async function runCheatTypeAnalysis(
    scenarioSelectId,
    resultId,
    buttonId
) {
    const scenarioSelect = document.getElementById(
        scenarioSelectId
    );

    const resultBox = document.getElementById(resultId);
    const button = document.getElementById(buttonId);

    if (!scenarioSelect || !resultBox || !button) {
        return;
    }

    const selectedScenario = scenarioSelect.value;
    const payload = cheatTypeScenarios[selectedScenario];

    if (!payload) {
        resultBox.textContent = "Invalid scenario selected.";
        return;
    }

    button.disabled = true;
    resultBox.textContent = "Analyzing gameplay indicators...";

    try {
        const response = await fetch(
            "/api/anti-cheat/cheat-types",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error
                    ? String(data.error)
                    : "Analysis request failed."
            );
        }

        const categories = data.detected_categories.length
            ? data.detected_categories.join(", ")
            : "None";

        const signals = data.detections.flatMap(
            item => item.signals
        );

        resultBox.textContent = [
            "Risk Level: " + data.risk_level,
            "Suspicious: " + (
                data.suspicious ? "YES" : "NO"
            ),
            "Detected Categories: " + categories,
            "Signals: " + (
                signals.length
                    ? signals.join(", ")
                    : "No suspicious indicators"
            ),
            "",
            data.note
        ].join("\n");

    } catch (error) {
        resultBox.textContent =
            "Analysis Error: " + error.message;
    } finally {
        button.disabled = false;
    }
}

const cheatTypeButtonBindings = [
    {
        buttonId: "aimbotAnalyzeButton",
        selectId: "aimbotScenario",
        resultId: "aimbotResult"
    },
    {
        buttonId: "wallhackAnalyzeButton",
        selectId: "wallhackScenario",
        resultId: "wallhackResult"
    },
    {
        buttonId: "automationAnalyzeButton",
        selectId: "automationScenario",
        resultId: "automationResult"
    }
];

cheatTypeButtonBindings.forEach(binding => {
    const button = document.getElementById(
        binding.buttonId
    );

    if (button) {
        button.addEventListener("click", () => {
            runCheatTypeAnalysis(
                binding.selectId,
                binding.resultId,
                binding.buttonId
            );
        });
    }
});


// ==========================================
// Blockchain-Style Asset Ledger Verification
// ==========================================

const verifyBlockchainLedgerButton = document.getElementById(
    "verifyBlockchainLedgerButton"
);

const blockchainLedgerResult = document.getElementById(
    "blockchainLedgerResult"
);

if (verifyBlockchainLedgerButton && blockchainLedgerResult) {
    verifyBlockchainLedgerButton.addEventListener(
        "click",
        async () => {
            verifyBlockchainLedgerButton.disabled = true;

            blockchainLedgerResult.textContent =
                "Verifying blockchain-style asset ledger...";

            try {
                const response = await fetch(
                    "/api/assets/blockchain-ledger",
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        "Ledger verification request failed. HTTP " +
                        response.status
                    );
                }

                const data = await response.json();
                const verification = data.verification;

                if (!verification) {
                    throw new Error(
                        "Invalid ledger verification response."
                    );
                }

                const resultLines = [
                    "Status: " + verification.status,
                    "Ledger Valid: " + (
                        verification.ledger_valid ? "YES" : "NO"
                    ),
                    "Records Checked: " +
                        verification.records_checked
                ];

                if (verification.failed_record !== undefined) {
                    resultLines.push(
                        "Failed Record: " +
                        verification.failed_record
                    );
                }

                if (verification.ledger_type) {
                    resultLines.push(
                        "Ledger Type: " +
                        verification.ledger_type
                    );
                }

                if (verification.note) {
                    resultLines.push(
                        "",
                        "Note: " + verification.note
                    );
                }

                blockchainLedgerResult.textContent =
                    resultLines.join("\n");

            } catch (error) {
                blockchainLedgerResult.textContent =
                    "Ledger Verification Error: " +
                    error.message;

            } finally {
                verifyBlockchainLedgerButton.disabled = false;
            }
        }
    );
}