# Day 9 — Examiner Demonstration Guide

**Environment:** Development demonstration only
**Objective status:** 5 VERIFIED, 13 PARTIAL
**Production claim:** None

## Recommended demonstration sequence

1. **Repository and tests** — show synchronized `7f1495e`, the recorded
   269/269 full regression, final 235/235 cross-module run, JavaScript syntax
   PASS, pip check PASS and Bandit 0 High / 0 Medium / 6 Low.
2. **Anti-cheat and marketplace** — demonstrate synthetic legitimate and
   suspicious cases. Explain that generic suspicious behavior uses a small ML
   model while named cheat categories and fraud decisions are bounded prototype
   logic.
3. **Assets** — register a synthetic asset, verify ownership, scan duplicates
   and show ledger integrity. State explicitly that this is a local hash-linked
   ledger, not a deployed blockchain.
4. **Identity and privacy** — use synthetic identity data, show successful and
   rejected login, consent allow/deny, and the automated biometric consent and
   encryption evidence. Do not use real biometric or personal data.
5. **Infrastructure** — show action validation, invalid packet rejection and
   simulated threat responses. Explain that rate limiting is application-layer,
   not comprehensive network DDoS protection.
6. **Moderation** — show text/child-safety controls if completing the remaining
   browser checks, then show prerecorded-WAV evidence at
   `screenshots/Day9_Real_Voice_Transcription_Moderation_PASSED.png`. Explain the
   imperfect transcript and that live audio streaming is not implemented.
7. **Stereo regression** — explain the normalized import namespaces and the
   permanent test proving stereo 16 kHz, 16-bit PCM returns sanitized HTTP 400
   with temporary upload cleanup.
8. **DevSecOps and limitations** — show the CI workflow and diagrams. State that
   CI has no deployment job and that Run 17 evidence, Run 19 authentication,
   full disaster recovery, Vosk checksum reproducibility and current production
   status remain unverified.
9. **Recovery boundary** — show 167 restored tracked files, zero checksum
   mismatches, regenerated models and four HTTP 200 routes; state explicitly
   that this is not EC2 disaster recovery.

## Evidence boundaries

- Actual-browser evidence is bounded to the controls recorded in
  `docs/day9_dashboard_testing_evidence.md`.
- Automated Flask tests are not visual browser evidence.
- Kernel behavior is a user-space audit simulation, not kernel enforcement.
- The ledger is local, not a public or deployed blockchain.
- Do not claim production readiness or complete Topic 137 compliance.
