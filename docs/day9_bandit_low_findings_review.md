# Day 9 — Bandit Low-Severity Findings Review

**Evidence date:** 1 November 2026
**Verified scan result:** 0 High, 0 Medium, 6 Low
**Scope:** Documentation-only risk review; no source changes

## Evidence boundary

The current Day 9 result is recorded in `docs/day9_final_testing_evidence.md`.
The checked-in `reports/bandit_report.txt` is older and contains only two Low
findings from a smaller 2,100-line scan; it must not be presented as the complete
Day 9 six-finding output. The six-finding locations and contextual review are
recorded in `docs/day7_devsecops_testing_evidence.md` and were cross-checked
against the current source.

## Findings and risk decisions

| Findings | Location | Scope | Risk assessment | Existing mitigation | Decision |
|---:|---|---|---|---|---|
| 2 | `src/devsecops/security_pipeline.py` | Bandit flags the `subprocess` import and execution | **Low / bounded development-tool risk.** Commands are defined by the script rather than accepted from an HTTP request or shell string. `shell=True` is not used. A future change that accepts untrusted command elements would materially increase risk. | Fixed argument lists, `cwd` fixed to repository root, no shell invocation, return-code handling | **Accept for frozen educational prototype; review if command inputs become dynamic.** |
| 2 | `src/devsecops/generate_dashboard_report.py` | Bandit flags the `subprocess` import and execution | **Low / bounded report-generation risk.** The `CHECKS` list is code-defined; no reviewed path from dashboard/API input to the command list was identified. `shell=True` is not used. | Fixed check definitions, fixed repository working directory, 180-second timeout, captured output and error handling | **Accept for frozen educational prototype; restrict execution to trusted development/CI environments.** |
| 2 | `src/identity_security/authentication.py` | Demonstration password passed to registration and login in the `__main__` example | **Low demonstration-secret risk.** The value is visible source code and must never be treated as a secret or reused for a real account. It is outside the imported Flask request path unless the module is run directly. | Demonstration-only block, password hashing for stored credentials, project warning against real credentials | **Accept only as synthetic demonstration data; never reuse or present it as a credential.** |

## Mitigation and monitoring

- Keep DevSecOps command lists code-defined and never concatenate user input.
- Continue avoiding `shell=True` and preserve explicit timeouts where present.
- Run DevSecOps scripts only in trusted development or CI environments with
  least-privilege permissions.
- Treat the demonstration password as public sample text; do not use it for any
  real identity, service or deployment.
- Rerun Bandit after any approved source change and reassess findings if their
  data flow or execution context changes.
- Preserve the six findings in submission evidence rather than suppressing them
  without a documented justification.

## Conclusion

The six findings are **reviewed residual Low risks**, not evidence of zero risk.
No confirmed command-injection path was identified in the reviewed fixed-command
scripts, and the password findings concern a direct-execution demonstration.
Risk acceptance is appropriate only for the frozen educational prototype scope;
production use would require a separate security review and removal or stronger
isolation of demonstration behavior.
