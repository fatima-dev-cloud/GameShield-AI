# Day 9 Task 9.3 — Deployment, Backup and Recovery Evidence Verification

**Verification date:** 1 November 2026
**Method:** Development-repository review only
**Branch/commit:** `development` at `6fe3693`
**Production accessed:** No

## Scope and safety boundary

This verification reviewed existing Day 8 documentation, architecture files
and screenshots stored in the development repository. It did not access the
production EC2 host, public URL, AWS APIs, GitHub, services, certificates, AMI,
snapshot, Nginx, Gunicorn or systemd. No deployment, recovery operation,
service check or external traffic test was performed during Day 9.

This report therefore verifies repository evidence, not current production or
AWS state.

## Evidence inspected

- `docs/day8_deployment_evidence.md`
- `docs/diagrams/aws_network_architecture.md`
- deployment and recovery sections in `README.md`
- the local `screenshots/Day8_*.png` inventory
- `.github/workflows/security.yml`

Read-only commands included:

```bash
find screenshots -maxdepth 1 -type f -name 'Day8_*.png' -printf '%f\n' | sort
file screenshots/Day8_Final_Deployment_Safety_Check_PASS.png
file screenshots/Day8_Latest_Production_Deployment_PASS.png
file screenshots/Day8_Live_Production_API_Security_Verification.png
file screenshots/Day8_GameShield_AI_Live_Public_Dashboard.png
rg -n -i "backup|restore|recovery|AMI|snapshot|certificate|https|production" \
  docs/day8_deployment_evidence.md \
  docs/diagrams/aws_network_architecture.md README.md
```

## Repository evidence results

| Area | Status | Repository evidence | Limitation |
|---|---|---|---|
| Day 8 screenshot inventory | **PASS** | 38 files matching `screenshots/Day8_*.png` are present | File presence and PNG format do not authenticate the depicted external state. |
| Deployment evidence record | **PASS for document presence** | Day 8 records HTTPS dashboard/API checks, Nginx/Gunicorn state and external browser access | These production claims were not rerun on Day 9; current production state is unverified. |
| HTTPS/certificate evidence | **PARTIAL** | Day 8 records HTTP 301, HTTPS 200, certificate validation, renewal timer and dry-run success | Recorded expiry was 6 November 2026. Day 9 did not contact the host or certificate authority. |
| Voice deployment evidence | **PARTIAL** | Day 8 records a silent WAV returning HTTP 200 through the configured Vosk pipeline | Spoken-word recognition and live voice streaming were not demonstrated. |
| Backup artifact record | **PARTIAL** | Day 8 records encrypted AMI `ami-0382db79c8d33e33f` and snapshot `snap-08e5ee70d7f2e1c81` | AWS existence, encryption and restorability were not checked on Day 9. The running root volume was documented as unencrypted. |
| File-level isolated recovery | **PASS for recorded Day 8 scope** | Day 8 records file comparison, restored entry point/data and Flask 200 responses for `/`, `/dashboard` and `/api/status` | No command transcript or dedicated recovery screenshot was identified. Full EC2 recovery remains unverified. |
| Full disaster recovery | **UNVERIFIED** | Day 8 explicitly says it was not verified | No instance-level restore, network recovery or complete functional recovery evidence exists. |
| CI evidence | **PARTIAL** | Day 8 text records Run #17 as successful. Day 7 text plus matching Run 16 screenshots authenticate an earlier successful CI run. A Run 19-named file is present. | Run 16 supports the general CI-capability claim but does not prove Run 17. Run 19 content remains unverified. Neither substitutes for the missing Run 17 screenshot. No external GitHub check was performed. |

## Evidence-reference inconsistency

Four of the five filenames listed in the Day 8 evidence section are present and
valid PNG files:

- `Day8_Final_Deployment_Safety_Check_PASS.png`
- `Day8_Latest_Production_Deployment_PASS.png`
- `Day8_Live_Production_API_Security_Verification.png`
- `Day8_GameShield_AI_Live_Public_Dashboard.png`

The cited `Day8_GitHub_Actions_Run17_Latest_Commit_SUCCESS.png` is absent. The
repository instead contains other CI screenshots, including
`Day8_Final_GitHub_Actions_CI_SUCCESS.png`,
`Day8_Final_GitHub_Actions_Run19_SUCCESS.png` and Run 16 detail screenshots.
Run 16 supports only the narrower claim that the security workflow succeeded
on an earlier documented commit. The Run 19-named file remains unverified from
the available local evidence. Neither file may be relabelled or treated as the
missing Run 17 artifact.

## Conclusion

**Task 9.3 status: PARTIAL.** Deployment, backup and isolated application-level
recovery claims are documented with a substantial local screenshot inventory.
Day 9 confirms those repository artifacts without touching production. Full
disaster recovery, current production/certificate state, AWS backup existence
and the specifically cited Run 17 screenshot remain unverified.
