# Model, Dataset, and Governance Record

## Model and dataset scope

The tracked `data/player_behavior.csv` and
`data/moderation_dataset.csv` files are small synthetic educational datasets.
Training reported 30 records or messages and deterministic nine-item evaluation
splits. The reported 100% anti-cheat and 77.78% moderation results demonstrate
pipeline execution only; they are not production accuracy, fairness, or
generalization evidence.

The generated Joblib models are ignored by Git and are reproducibly created by:

- `src/anti_cheat/train_model.py`
- `src/content_moderation/train_moderation_model.py`

The external Vosk model is also ignored. Its archive SHA256 was calculated
after download from the documented official HTTPS URL. No independent
published checksum was established. Fourteen extracted files matched the
configured development model by relative path and SHA256.

No formal project model cards, dataset provenance/licensing attestation, bias
analysis, drift monitoring, production telemetry validation, or independent
model evaluation were found. Voice recognition processes prerecorded WAV files
rather than a live audio stream.

## Governance decisions requiring external authority

- **Licence:** no project licence is selected. The copyright holder or
  institution must choose and approve one before a licence file is added.
- **Contribution policy:** no external-contribution or maintainer-approval
  process has been authorized.
- **Security reporting:** no private reporting address or institutional
  response commitment has been supplied; neither is invented here.
- **Dataset provenance:** the datasets are described as synthetic, but a formal
  provenance and licensing attestation requires the human author.
- **Institutional packaging:** submission-checklist, official-source inclusion,
  and AI-policy requirements require institutional confirmation.

These are external governance decisions, not hidden application defects. Their
effect on submission depends on the applicable institutional rules.
