from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from anti_cheat import detector
from asset_security import asset_registry
from asset_security import fraud_detector
from content_moderation import child_safety
from content_moderation import moderator
from identity_security import authentication
from identity_security import biometric_protection
from identity_security import privacy_controls
from infrastructure_security import rate_limiter
from infrastructure_security import secure_netcode
from infrastructure_security import server_validation
from infrastructure_security import threat_response


def _assert_within(path, parent):
    resolved_path = path.resolve()
    resolved_parent = parent.resolve()

    try:
        resolved_path.relative_to(resolved_parent)
    except ValueError:
        raise AssertionError(
            f"Test path escaped tmp_path: {resolved_path}"
        ) from None


@pytest.fixture(autouse=True)
def isolate_persistent_file_paths(tmp_path, monkeypatch):
    test_logs = tmp_path / "logs"
    test_data = tmp_path / "data"
    test_config = tmp_path / "config"

    infrastructure_log = (
        test_logs / "infrastructure_security.log"
    )
    content_moderation_log = (
        test_logs / "content_moderation.log"
    )
    identity_security_log = (
        test_logs / "identity_security.log"
    )

    replacements = [
        (
            detector,
            "LOG_FILE",
            test_logs / "anti_cheat.log",
        ),
        (
            fraud_detector,
            "LOG_FILE",
            test_logs / "marketplace_fraud.log",
        ),
        (
            asset_registry,
            "ASSET_FILE",
            test_data / "virtual_assets.json",
        ),
        (
            asset_registry,
            "LOG_FILE",
            test_logs / "asset_security.log",
        ),
        (
            secure_netcode,
            "KEY_FILE",
            test_config / "netcode.key",
        ),
        (
            secure_netcode,
            "LOG_FILE",
            infrastructure_log,
        ),
        (
            server_validation,
            "LOG_FILE",
            infrastructure_log,
        ),
        (
            rate_limiter,
            "LOG_FILE",
            infrastructure_log,
        ),
        (
            threat_response,
            "LOG_FILE",
            infrastructure_log,
        ),
        (
            child_safety,
            "LOG_FILE",
            content_moderation_log,
        ),
        (
            moderator,
            "LOG_FILE",
            content_moderation_log,
        ),
        (
            authentication,
            "USER_FILE",
            test_data / "users.json",
        ),
        (
            authentication,
            "LOG_FILE",
            identity_security_log,
        ),
        (
            privacy_controls,
            "PRIVACY_FILE",
            test_data / "privacy_settings.json",
        ),
        (
            privacy_controls,
            "LOG_FILE",
            identity_security_log,
        ),
        (
            biometric_protection,
            "KEY_FILE",
            test_config / "biometric.key",
        ),
        (
            biometric_protection,
            "ENCRYPTED_DATA_FILE",
            test_data / "protected_biometrics.dat",
        ),
        (
            biometric_protection,
            "LOG_FILE",
            identity_security_log,
        ),
    ]

    assert len(replacements) == 18

    for module, attribute, replacement_path in replacements:
        assert isinstance(replacement_path, Path)
        _assert_within(replacement_path, tmp_path)

        monkeypatch.setattr(
            module,
            attribute,
            replacement_path,
        )
