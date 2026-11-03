# Security Findings and Limitations

The detailed review is `docs/day9_bandit_low_findings_review.md`.

The current Bandit scan of `src/` reported 4,391 lines and:

| Severity | Findings |
|---|---:|
| High | 0 |
| Medium | 0 |
| Low | 6 |

The six Low findings comprise four subprocess-related findings in fixed-command
DevSecOps scripts and two public demonstration-password findings. They were not
suppressed or claimed as fixed. They remain accepted only as documented
educational-prototype residual risks.

Zero High/Medium findings does not mean zero vulnerabilities. Material security
limitations include no kernel enforcement, deployed blockchain, network-layer
DDoS proof, production game netcode, VR/AR integration, live voice stream,
trusted Vosk checksum, deployment gates, signed artifacts, SBOM or verified AWS
recovery.
