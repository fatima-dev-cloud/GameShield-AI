# Day 9 AI-Use Disclosure — Testing Addendum

**Date:** 1 November 2026
**Applies to:** `docs/day9_ai_use_disclosure.md`

This addendum preserves the history of one stale statement that previously
appeared in the primary Day 9 disclosure. The primary
`docs/day9_ai_use_disclosure.md` has now been corrected to include the
subsequent authorized testing and Codex verification work.

The verified development results are:

- Full regression: 268/268 tests passed in 5.16 seconds.
- Dependency consistency: `pip check` passed with no broken requirements.
- Bandit: 0 High, 0 Medium and 6 Low findings.
- Focused dashboard/API selection: 126/126 tests passed in 3.62 seconds.
- Dashboard JavaScript syntax: `node --check` passed.

Codex also inspected the dashboard template, JavaScript API connections, Flask
routes and test isolation, and created:

- `docs/day9_final_testing_evidence.md`
- `docs/day9_dashboard_testing_evidence.md`
- `docs/day9_deployment_recovery_verification.md`
- `docs/day9_final_acceptance_report.md`

The safety disclosure remains unchanged: Codex did not access production,
deploy, restart services, delete files, modify application code, commit or push.
No contribution percentage is claimed. Historical ChatGPT scope and final human
attribution still require confirmation by the student/author.

Consolidation status: **PRIMARY DISCLOSURE CORRECTED**.

This addendum remains as an audit trail. Final human confirmation of historical
ChatGPT scope, personal attribution and institutional AI-use compliance is still
pending; no contribution percentage has been invented.
