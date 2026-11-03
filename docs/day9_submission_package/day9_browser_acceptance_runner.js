"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.DAY9_BASE_URL || "http://127.0.0.1:18766";
const root = process.env.DAY9_REPOSITORY_ROOT || process.cwd();
const screenshotDir = path.join(root, "screenshots", "day9");
const resultPath = path.join(
    root,
    "docs",
    "day9_submission_package",
    "browser_acceptance_results.json"
);
const audioPath = process.env.DAY9_TEST_WAV;

if (!audioPath || !fs.existsSync(audioPath)) {
    throw new Error("DAY9_TEST_WAV must identify an existing test WAV file");
}

fs.mkdirSync(screenshotDir, { recursive: true });

const results = {
    base_url: baseUrl,
    executed_at_utc: new Date().toISOString(),
    browser: {},
    console_errors: [],
    page_errors: [],
    request_failures: [],
    http_errors: [],
    checks: {},
    workflows: {},
    screenshots: [],
};

function screenshotPath(filename) {
    const output = path.join(screenshotDir, filename);
    results.screenshots.push(path.relative(root, output));
    return output;
}

async function clickForApi(page, button, result, endpoint) {
    const [response] = await Promise.all([
        page.waitForResponse(
            (candidate) => candidate.url().includes(endpoint),
            { timeout: 15000 }
        ),
        page.locator(button).click(),
    ]);
    // The demo intentionally permits 10 requests per 10 seconds. Pace the
    // workflow like a human operator instead of burst traffic.
    await page.waitForTimeout(1100);
    const text = (await page.locator(result).innerText()).trim();
    if (!response.ok()) {
        throw new Error(`${endpoint} returned HTTP ${response.status()}: ${text}`);
    }
    return { status: response.status(), result: text };
}

async function run() {
    const browser = await chromium.launch({ headless: true });
    results.browser.version = browser.version();

    const desktop = await browser.newContext({
        viewport: { width: 1440, height: 1000 },
        colorScheme: "light",
    });
    const page = await desktop.newPage();

    page.on("console", (message) => {
        if (message.type() === "error") {
            results.console_errors.push(message.text());
        }
    });
    page.on("pageerror", (error) => results.page_errors.push(error.message));
    page.on("requestfailed", (request) => {
        results.request_failures.push({
            url: request.url(),
            error: request.failure()?.errorText || "unknown",
        });
    });
    page.on("response", (response) => {
        if (response.status() >= 400) {
            results.http_errors.push({
                url: response.url(),
                status: response.status(),
            });
        }
    });

    const dashboardResponse = await page.goto(`${baseUrl}/dashboard`, {
        waitUntil: "networkidle",
        timeout: 30000,
    });
    results.checks.dashboard_http = dashboardResponse.status();
    results.checks.title = await page.title();
    results.checks.desktop_no_horizontal_overflow = await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth
    );
    results.checks.navigation_links = await page.locator(".gs-nav-link").count();

    await page.screenshot({
        path: screenshotPath("Day9_Desktop_Overview.png"),
        fullPage: true,
    });

    for (const target of [
        "#gs-overview",
        "#gs-anticheat",
        "#gs-assets",
        "#gs-identity",
        "#gs-infrastructure",
        "#moderation-panel",
        "#devsecops-panel",
    ]) {
        await page.locator(`a[href='${target}']`).click();
        await page.waitForTimeout(75);
        if ((await page.evaluate(() => window.location.hash)) !== target) {
            throw new Error(`Navigation failed for ${target}`);
        }
    }
    results.checks.navigation = "PASS";

    const focusSequence = [];
    await page.locator("body").click({ position: { x: 5, y: 5 } });
    for (let index = 0; index < 12; index += 1) {
        await page.keyboard.press("Tab");
        focusSequence.push(
            await page.evaluate(() => {
                const active = document.activeElement;
                return active?.id || active?.getAttribute("href") || active?.tagName;
            })
        );
    }
    results.checks.keyboard_focus_sequence = focusSequence;
    results.checks.keyboard_focus_distinct = new Set(focusSequence).size >= 6;

    await page.locator("#playerType").selectOption("cheater");
    results.workflows.anti_cheat = await clickForApi(
        page,
        "#analyzeButton",
        "#result",
        "/api/anti-cheat/analyze"
    );
    await page.locator("#sharingScenario").selectOption("suspicious");
    results.workflows.account_sharing = await clickForApi(
        page,
        "#sharingAnalyzeButton",
        "#sharingResult",
        "/api/anti-cheat/account-sharing"
    );
    await page.locator("#gs-anticheat").screenshot({
        path: screenshotPath("Day9_AntiCheat_Workflow.png"),
    });

    await page.locator("#transactionType").selectOption("suspicious");
    results.workflows.marketplace = await clickForApi(
        page,
        "#analyzeTransactionButton",
        "#transactionResult",
        "/api/marketplace/analyze"
    );
    const unique = Date.now().toString();
    await page.locator("#assetName").fill(`Day9 Browser Asset ${unique}`);
    await page.locator("#assetOwner").fill(`day9_owner_${unique}`);
    results.workflows.asset_register = await clickForApi(
        page,
        "#registerAssetButton",
        "#assetRegisterResult",
        "/api/assets/register"
    );
    results.workflows.asset_verify = await clickForApi(
        page,
        "#verifyAssetButton",
        "#assetVerifyResult",
        "/api/assets/verify"
    );
    results.workflows.ledger = await clickForApi(
        page,
        "#verifyBlockchainLedgerButton",
        "#blockchainLedgerResult",
        "/api/assets/blockchain-ledger"
    );
    await page.locator("#gs-assets").screenshot({
        path: screenshotPath("Day9_AssetSecurity_Workflow.png"),
    });

    const username = `day9_browser_${unique}`;
    const password = `Synthetic-${unique}!`;
    await page.locator("#identityUsername").fill(username);
    await page.locator("#identityPassword").fill(password);
    results.workflows.identity_register = await clickForApi(
        page,
        "#registerIdentityButton",
        "#identityRegisterResult",
        "/api/identity/register"
    );
    await page.locator("#loginUsername").fill(username);
    await page.locator("#loginPassword").fill(password);
    results.workflows.identity_login = await clickForApi(
        page,
        "#loginIdentityButton",
        "#identityLoginResult",
        "/api/identity/login"
    );
    await page.locator("#privacyUserId").fill(username);
    await page.locator("#privacyDataType").selectOption("eye_tracking");
    await page.locator("#privacyAllowed").selectOption("true");
    results.workflows.privacy_eye_tracking = await clickForApi(
        page,
        "#updatePrivacyButton",
        "#privacyResult",
        "/api/identity/privacy"
    );
    await page.locator("#privacyDataType").selectOption("motion_tracking");
    results.workflows.privacy_motion_tracking = await clickForApi(
        page,
        "#updatePrivacyButton",
        "#privacyResult",
        "/api/identity/privacy"
    );
    await page.locator("#biometricUserId").fill(username);
    results.workflows.biometric = await clickForApi(
        page,
        "#protectBiometricButton",
        "#biometricResult",
        "/api/identity/biometric/protect"
    );
    await page.locator("#gs-identity").screenshot({
        path: screenshotPath("Day9_IdentityPrivacy_Workflow.png"),
    });

    results.workflows.server_validation = await clickForApi(
        page,
        "#validateActionButton",
        "#actionValidationResult",
        "/api/infrastructure/validate-action"
    );
    await page.locator("#threatSeverity").selectOption("high");
    results.workflows.threat_response = await clickForApi(
        page,
        "#threatResponseButton",
        "#threatResponseResult",
        "/api/infrastructure/threat-response"
    );
    await page.locator("#gs-infrastructure").screenshot({
        path: screenshotPath("Day9_InfrastructureSecurity_Workflow.png"),
    });

    await page.locator("#moderationMessage").fill("You are terrible and I hate you");
    results.workflows.text_moderation = await clickForApi(
        page,
        "#moderateTextButton",
        "#moderationTextResult",
        "/api/moderation/text"
    );
    await page.locator("#childUserAge").fill("10");
    await page.locator("#childContentRating").selectOption("ADULT");
    results.workflows.child_safety = await clickForApi(
        page,
        "#checkChildSafetyButton",
        "#childSafetyResult",
        "/api/moderation/child-safety"
    );
    await page.locator("#multiplayerMessage").fill("Good teamwork everyone");
    results.workflows.realtime_text = await clickForApi(
        page,
        "#moderateMultiplayerButton",
        "#multiplayerModerationResult",
        "/api/moderation/realtime"
    );
    await page.locator("#voiceAudioFile").setInputFiles(audioPath);
    results.workflows.voice = await clickForApi(
        page,
        "#moderateVoiceButton",
        "#voiceModerationResult",
        "/api/moderation/voice"
    );
    await page.locator("#moderation-panel").screenshot({
        path: screenshotPath("Day9_Moderation_Workflow.png"),
    });

    results.workflows.devsecops = await clickForApi(
        page,
        "#loadDevsecopsReportButton",
        "#devsecopsReportResult",
        "/api/devsecops/report"
    );
    await page.locator("#devsecops-panel").screenshot({
        path: screenshotPath("Day9_DevSecOps_Workflow.png"),
    });

    const mobile = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
    });
    const mobilePage = await mobile.newPage();
    const mobileResponse = await mobilePage.goto(`${baseUrl}/dashboard`, {
        waitUntil: "networkidle",
        timeout: 30000,
    });
    results.checks.mobile_http = mobileResponse.status();
    results.checks.mobile_no_horizontal_overflow = await mobilePage.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth
    );
    await mobilePage.screenshot({
        path: screenshotPath("Day9_Mobile_Responsive_Dashboard.png"),
        fullPage: true,
    });

    await mobile.close();
    await desktop.close();
    await browser.close();

    results.pass =
        results.checks.dashboard_http === 200 &&
        results.checks.mobile_http === 200 &&
        results.checks.desktop_no_horizontal_overflow &&
        results.checks.mobile_no_horizontal_overflow &&
        results.checks.keyboard_focus_distinct &&
        results.console_errors.length === 0 &&
        results.page_errors.length === 0 &&
        results.request_failures.length === 0 &&
        results.http_errors.length === 0;

    fs.writeFileSync(resultPath, `${JSON.stringify(results, null, 2)}\n`);
    console.log(JSON.stringify(results, null, 2));
    if (!results.pass) {
        process.exitCode = 1;
    }
}

run().catch((error) => {
    results.fatal_error = error.stack || error.message;
    fs.writeFileSync(resultPath, `${JSON.stringify(results, null, 2)}\n`);
    console.error(error);
    process.exitCode = 1;
});
