# Repository and Reproducibility Report

The detailed audit is `docs/day9_repository_audit.md`.

`README.md`, dependency files, source, tests, synthetic datasets, six
architecture documents, the CI workflow, Day 3–9 evidence and screenshots are
present. Current `pip check` reported no broken requirements.
`.github/workflows/security.yml` provides CI security checks but no deployment
job.

Generated anti-cheat and moderation models are ignored and must be regenerated.
The Vosk model is also ignored. `docs/voice_setup.md` documents its official
model name, expected directory and `VOSK_MODEL_PATH`; existing development
Gunicorn evidence also required `PYTHONPATH`.

| Reproducibility item | Status |
|---|---|
| Tracked source, tests and documentation | VERIFIED |
| Prepared-environment dependency consistency | VERIFIED |
| Current regression | VERIFIED — 269/269 |
| Demonstration-model generation | DOCUMENTED |
| Clean-clone dependency/model setup | PARTIAL |
| Trusted Vosk checksum | NOT VERIFIED |
| Production reproduction | NOT PERFORMED |

No checksum is invented. Model cards, comprehensive dataset provenance, a
licence and contribution/security policies were not found; institutional rules
determine whether they are mandatory.
