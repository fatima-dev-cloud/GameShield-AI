# Day 9 Submission Evidence Inventory

Every artifact in the included tables was checked for existence in the local
development repository on 2 November 2026. A status of **PRESENT** verifies the
repository path, not the truth of an external system depicted by a screenshot.

## Core submission artifacts

| Artifact | Repository path | Status |
|---|---|---|
| Project overview and setup | `README.md` | PRESENT |
| Official-requirement mapping | `docs/day9_final_evidence_matrix.md` | PRESENT — 5 VERIFIED / 13 PARTIAL |
| Test and security results | `docs/day9_final_testing_evidence.md` | PRESENT |
| Dashboard/API acceptance evidence | `docs/day9_dashboard_testing_evidence.md` | PRESENT — PARTIAL |
| Deployment and recovery evidence | `docs/day9_deployment_recovery_verification.md` | PRESENT — PARTIAL |
| Repository audit | `docs/day9_repository_audit.md` | PRESENT — PARTIAL |
| AI-use disclosure | `docs/day9_ai_use_disclosure.md` | PRESENT — human confirmation pending |
| AI-use disclosure audit trail | `docs/day9_ai_use_disclosure_addendum.md` | PRESENT |
| Six Low Bandit findings review | `docs/day9_bandit_low_findings_review.md` | PRESENT |
| Existing examiner guide | `docs/day9_examiner_demonstration_guide.md` | PRESENT |
| Submission manifest | `docs/day9_submission_manifest.md` | PRESENT |

## Implementation and testing sources

| Evidence group | Repository path | Status |
|---|---|---|
| Application implementation | `src/` | PRESENT |
| Automated tests | `tests/` | PRESENT |
| Runtime dependencies | `requirements.txt` | PRESENT |
| Development dependencies | `requirements-dev.txt` | PRESENT |
| CI security workflow | `.github/workflows/security.yml` | PRESENT — CI only; no deployment job |
| Topic 137 local objective tracker | `docs/day6_topic137_objective_tracker.md` | PRESENT |
| DevSecOps evidence | `docs/day7_devsecops_testing_evidence.md` | PRESENT |
| Day 8 deployment evidence | `docs/day8_deployment_evidence.md` | PRESENT |
| Voice setup instructions | `docs/voice_setup.md` | PRESENT |

## Architecture evidence

All six referenced Markdown diagrams are present:

- `docs/diagrams/system_architecture.md`
- `docs/diagrams/security_architecture.md`
- `docs/diagrams/data_flow_diagram.md`
- `docs/diagrams/aws_network_architecture.md`
- `docs/diagrams/devsecops_workflow.md`
- `docs/diagrams/kernel_event_simulation_architecture.md`

## Screenshot evidence

- 38 files matching `screenshots/Day8_*.png` are present.
- `screenshots/Day9_Real_Voice_Transcription_Moderation_PASSED.png` is present
  and tracked. It supports the bounded prerecorded-WAV voice demonstration.
- Run 16 detail screenshots are present and support only the earlier Run 16 CI
  result.
- `screenshots/Day8_Final_GitHub_Actions_Run19_SUCCESS.png` is present, but its
  depicted external result remains unverified.

## Missing or unauthenticated evidence

- `screenshots/Day8_GitHub_Actions_Run17_Latest_Commit_SUCCESS.png` is absent.
  Run 16 and the Run 19-named file must not be substituted for it.
- The official Topic 137 v0.1 PDF is not verified as stored in the repository.
- Full EC2/AWS disaster recovery, current production state, certificate state
  and backup restorability were not verified during Day 9.
- Clean-clone Vosk acquisition and a trusted model checksum remain unresolved.
- Model cards, dataset provenance, a licence, contribution/security policies
  and an institution-supplied submission checklist/presentation were not found.
- Several objective-specific visual demonstrations remain incomplete, as
  recorded in the evidence matrix and dashboard report.
