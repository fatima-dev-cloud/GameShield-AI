# Day 8 — AWS Deployment and Final Documentation Evidence

Date: 30 October 2026

## 1. Production Deployment

Project: GameShield AI
Platform: AWS EC2, Ubuntu 24.04
Application: Flask
Application server: Gunicorn
Reverse proxy: Nginx

Public demonstration URL:
http://3.115.183.249/dashboard

Production release directory:
/home/ubuntu/gameshield-release-day8

Deployment method:
An isolated release directory was prepared from the
GitHub development branch.

A separate Python virtual environment was installed.

Existing production models, encryption keys and
persistent application data were retained.

The systemd application service was updated to use
the isolated release directory.

## 2. Deployment Verification

Verified results:

- Gunicorn service: active
- Nginx service: active
- Homepage: HTTP 200
- Dashboard: HTTP 200
- API status: HTTP 200
- Dashboard CSS: HTTP 200
- Dashboard JavaScript: HTTP 200
- Gunicorn binding: 127.0.0.1:8000
- Nginx HTTP listener: port 80
- External Windows Chrome dashboard access: successful

The original dashboard design was preserved.

## 3. GitHub and CI/CD

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

## 4. Backup and Recovery

Original production service configuration was backed up.

An AWS machine image backup was created.

Encrypted AMI:
ami-0382db79c8d33e33f

Encrypted snapshot:
snap-08e5ee70d7f2e1c81

An isolated recovery instance successfully passed
AWS EC2 infrastructure status checks.

Application-level recovery was not verified because
SSH and SSM access were unavailable.

The temporary recovery instance was terminated.

The encrypted backup does not establish that the
currently running production root volume is encrypted.

## 5. Security Limitations

The demonstration currently uses HTTP.

HTTPS/TLS has not been configured.

The public deployment must not be used to transmit
real credentials, biometric data or sensitive records.

Security headers require further configuration.

The Vosk speech recognition model is not currently
configured in the production application service.

Voice moderation was verified in development, but
production voice transcription remains unverified.

The project is an educational cybersecurity prototype,
not a production-hardened security service.

## 6. Evidence

- Day8_Final_Deployment_Safety_Check_PASS.png
- Day8_Latest_Production_Deployment_PASS.png
- Day8_Live_Production_API_Security_Verification.png
- Day8_GameShield_AI_Live_Public_Dashboard.png
- Day8_GitHub_Actions_Run17_Latest_Commit_SUCCESS.png

## 7. Conclusion

GameShield AI was deployed successfully to an existing
AWS EC2 instance.

The dashboard was accessible from an external browser.

The latest development commit passed the GitHub
Actions security workflow.

Backup artifacts and architecture documentation
are available.

Remaining security limitations are documented.
