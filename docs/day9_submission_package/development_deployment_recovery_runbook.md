# Development Deployment and Recovery Runbook

## Scope and verified boundary

This runbook covers the educational development deployment and disposable
local recovery demonstration. Day 9 verified a fresh clone, a new virtual
environment, dependency installation, model regeneration, 269 tests, and
loopback Gunicorn recovery from HTTP 200 to unavailable and back to HTTP 200.

It did not verify Nginx or systemd configuration, EC2, EBS, AMI, certificates,
production data, AWS networking, or backup restoration. AWS disaster recovery
remains unverified. No Nginx site file or systemd unit is tracked in this
repository; those platform configurations require separate authorized review.

## Installation prerequisites and order

```bash
git clone --branch development --single-branch https://github.com/fatima-dev-cloud/GameShield-AI.git
cd GameShield-AI
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python src/anti_cheat/train_model.py
python src/content_moderation/train_moderation_model.py
export PYTHONPATH="$PWD/src"
export VOSK_MODEL_PATH="$PWD/models/vosk/vosk-model-small-en-us-0.15"
gunicorn --bind 127.0.0.1:8000 --workers 1 app:app
```

The Vosk archive was downloaded from the documented official HTTPS URL and its
SHA256 was calculated locally as
`30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498`.
This is not an independently published trusted-checksum verification. Fourteen
extracted files matched the configured development model by path and SHA256.

## Backup prerequisites

Record the active commit, dependency versions, environment-variable names
without values, runtime-data locations, service/proxy configuration, and
storage-encryption state. Back up runtime data and configuration separately
from source. Verify readability and retention, and never overwrite the only
known-good backup. Keep secrets outside Git and evidence.

## Restoration order

1. Restore into an isolated target, not over the only working copy.
2. Restore and verify the reviewed source commit.
3. Create a new virtual environment and install pinned dependencies.
4. Restore reviewed configuration and secrets through the platform mechanism.
5. Regenerate demonstration models and restore only required runtime data with
   permissions preserved.
6. Download the Vosk model over HTTPS, calculate its checksum, and compare the
   extracted files.
7. Start Gunicorn on loopback and run health checks.
8. Attach reviewed service/proxy configuration only after loopback checks pass.
9. Exercise synthetic requests only; never use production user data.

## Health checks

Expected HTTP 200 paths are:

- `/`
- `/dashboard`
- `/api/status`
- `/api/devsecops/report`
- `/static/css/dashboard.css`
- `/static/js/dashboard.js`

Also confirm there is no startup traceback, required models load, temporary
uploads are removed, the browser console is clear, and the running commit
matches the approved commit.

## Rollback and data preservation

Keep traffic detached or roll back if startup fails, a health path is non-200,
configuration or model errors occur, data integrity differs, secrets appear in
output, or the approved commit cannot be verified. Stop only the new process,
preserve diagnostic logs, restore the recorded prior release/configuration,
and repeat health checks.

Copy data before transformation, preserve hashes, counts, and permissions,
avoid broad deletion, and redact sensitive output. Use only synthetic
identities and payloads for demonstration.

## Examiner recovery demonstration

1. Show the reviewed commit and disposable environment.
2. Start loopback-only Gunicorn and show `/api/status` returning HTTP 200.
3. Stop only that process and show a bounded connection failure.
4. Restart with the same reviewed configuration and show HTTP 200 recovery.
5. Show source integrity and cleanup.
6. State that this proves local application-process recovery only, not AWS
   disaster recovery.
