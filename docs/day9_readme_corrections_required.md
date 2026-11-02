# Day 9 — README Corrections Required

The README was reviewed on 1 November 2026. Initial patch-helper and fallback
attempts failed because of the documented `bwrap` restriction, malformed patch
input and unavailable Ruby runtime; those attempts made no changes.

The corrections below were subsequently applied successfully with Python 3.12.3
standard-library exact-match replacements. All old blocks were asserted in
memory before same-directory temporary files were written and atomically
replaced with permissions preserved.

Applied and verified corrections:

1. Replace the illustrative `CyberSecurityProject/` tree with the current
   `GameShield-AI/` structure. Explain that local `config/`, `logs/` and
   `models/` directories are generated/ignored, and show the broader `tests/`
   inventory rather than only two files.
2. Replace the obsolete `13 passed in 2.80s` result with the dated Day 9 result:
   268 collected and 268 passed in 5.16 seconds. Link
   `docs/day9_final_testing_evidence.md` and
   `docs/day9_dashboard_testing_evidence.md`.
3. Record Bandit as 0 High, 0 Medium and 6 Low, with a link to
   `docs/day9_bandit_low_findings_review.md`.
4. Label the public URL, service state, certificate expiry and browser results as
   historical Day 8 evidence, not current Day 9 verification.
5. Correct the statement that the production repository remained on clean
   `main`: Day 8 evidence says it was initially checked on `main` and later
   observed on `development` at `565afea`; the deployed application used a
   separate release directory.
6. Preserve the kernel-simulation and local-ledger limitations, and retain the
   statement that CI does not automatically deploy.
7. Make clean-clone voice setup explicit: generated Joblib models must be
   trained, the Vosk model must be acquired separately, and a trusted Vosk
   checksum has not been verified.

Consolidation status: **APPLIED AND VERIFIED**.

Validation completed:

- `git diff --check`: PASS.
- README local Markdown links: all resolved.
- File permissions: preserved.
- No source, test, model, dependency, CI or deployment file changed.

The official Topic 137 brief, clean-clone Vosk checksum evidence and current
external deployment state remain separate unresolved evidence items; they are
not README-edit failures.
