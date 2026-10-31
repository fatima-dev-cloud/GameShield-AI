# Day 8 — AWS Deployment and Final Documentation Evidence

Date: 31 October 2026

## 1. Production Deployment

Project: GameShield AI
Platform: AWS EC2, Ubuntu 24.04
Application: Flask
Application server: Gunicorn
Reverse proxy: Nginx

Public demonstration URL:
https://3.115.183.249/dashboard

Production release directory:
/home/ubuntu/gameshield-release-day8

Deployment method:
The existing production EC2 instance was reused. An isolated release
directory was prepared from the GitHub development branch; no new EC2
instance was required for the final deployment.

A separate Python virtual environment was installed.

Existing production models, encryption keys and
persistent application data were retained.

The systemd application service was updated to use
the isolated release directory.

The original production repository remained on `main` and its worktree
remained clean. An independent final Nginx configuration backup was created
at `/etc/nginx/gameshield-ai.day8-final-backup`.

## 2. Deployment Verification

Verified results:

- Gunicorn service: active
- Nginx service: active
- Public HTTP dashboard request: HTTP 301 redirect to HTTPS
- Public HTTPS dashboard: HTTP 200
- API status: HTTP 200
- Dashboard CSS: HTTP 200
- Dashboard JavaScript: HTTP 200
- Gunicorn binding: 127.0.0.1:8000
- Nginx: running with HTTP and HTTPS handling
- Gunicorn/systemd application service: running
- External Windows Chrome dashboard access: successful
- Public certificate validation with `curl`: successful
- ACME HTTP challenge path: accessible
- Production services remained active after the deployment changes

The original dashboard design was preserved.

## 3. HTTPS Certificate and Renewal

Let's Encrypt successfully issued a certificate for the public IP address.

| Check | Verified result |
|---|---|
| Certificate expiry | 6 November 2026 |
| HTTP-to-HTTPS behavior | HTTP 301 |
| HTTPS dashboard | HTTP 200 |
| Public `curl` certificate validation | Successful |
| Certbot automatic renewal timer | Enabled |
| `certbot renew --dry-run` | All simulated renewals succeeded |
| ACME HTTP challenge | Remains publicly accessible |

Because an IP-address certificate is short-lived, reliable automatic renewal
is an operational requirement. The renewal timer and challenge path must
continue to be monitored.

## 4. Production Voice Moderation Verification

The `vosk-model-small-en-us-0.15` speech-recognition model was installed in
the production release and configured through `VOSK_MODEL_PATH`.

The production voice moderation API was exercised with a one-second silent
PCM WAV file. It returned HTTP 200, an empty transcription, and `BLOCK` for
the resulting empty message. This verifies production model loading, WAV
handling, transcription orchestration, and moderation response behavior for
that silent fixture.

Actual spoken-word transcription has not yet been verified in production.
The silent-file result must not be presented as evidence of spoken-word
recognition accuracy or live voice-chat moderation.

## 5. GitHub and CI/CD

Repository:
https://github.com/fatima-dev-cloud/GameShield-AI

Branch: development

Verified commit: dc3ce5c

GitHub Actions workflow:
GameShield AI Security Pipeline

Run: #17
Status: SUCCESS
Duration: 44 seconds

The security-tests job completed successfully.

## 6. Backup and Recovery

Original production service configuration was backed up.

An AWS machine image backup was created.

Encrypted AMI:
ami-0382db79c8d33e33f

Encrypted snapshot:
snap-08e5ee70d7f2e1c81

Encrypted backup artifacts exist, but full EC2 disaster recovery has not
been verified. Earlier infrastructure checks do not establish successful
application-level restoration.

The encrypted backup does not establish that the
currently running production root volume is encrypted.
The running root EBS volume remains unencrypted.

## 7. Limitations and Claim Boundaries

- Full EC2 disaster recovery has not been verified.
- The root EBS volume remains unencrypted; encrypted backup artifacts exist.
- The short-lived IP-address certificate depends on reliable automatic
  renewal and continued ACME challenge availability.
- Public API security and production hardening must not be described as fully
  complete without additional evidence.
- Actual spoken-word transcription remains unverified in production.
- Original Topic 137 has 18 objectives; they must not be described as fully
  verified. See the [objective tracker](day6_topic137_objective_tracker.md).
- This remains an educational prototype, not a production-hardened security
  service. Real credentials, biometric data, and sensitive records should not
  be submitted to the public demonstration.

## 8. Evidence

- Day8_Final_Deployment_Safety_Check_PASS.png
- Day8_Latest_Production_Deployment_PASS.png
- Day8_Live_Production_API_Security_Verification.png
- Day8_GameShield_AI_Live_Public_Dashboard.png
- Day8_GitHub_Actions_Run17_Latest_Commit_SUCCESS.png

## 9. Conclusion

GameShield AI was deployed successfully to an existing
AWS EC2 instance.

The HTTPS dashboard was accessible from an external browser, and the HTTP
endpoint redirected to HTTPS.

The latest development commit passed the GitHub
Actions security workflow.

Encrypted backup artifacts and architecture documentation are available,
but they do not establish full disaster recovery or root-volume encryption.

Certificate renewal, production spoken-word transcription, disaster recovery,
public API hardening, and the remaining Topic 137 evidence gaps are explicitly
documented rather than claimed as complete.
