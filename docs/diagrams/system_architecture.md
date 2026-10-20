
# GameShield AI — System Architecture

## Overview

GameShield AI is an educational gaming and VR/AR security demonstration platform deployed on AWS EC2.

## Architecture Diagram

```mermaid
flowchart TD
    A["User / Chrome Browser"] --> B["Nginx Reverse Proxy"]
    B --> C["Gunicorn Application Server"]
    C --> D["Flask API - src/app.py"]

    D --> E["AI Anti-Cheat"]
    D --> F["Virtual Asset Security"]
    D --> G["Metaverse Identity Security"]
    D --> H["Gaming Infrastructure Security"]
    D --> I["Content Moderation"]
    D --> J["DevSecOps Reporting"]

    E --> K["Trained ML Model"]
    F --> L["Local Asset Registry"]
    G --> M["Identity and Privacy Controls"]
    H --> N["Validation and Threat Response"]
    I --> O["Moderation Model and Rules"]
    J --> P["Security Reports"]

    Q["GitHub Actions CI"] --> R["Automated Security Tests"]
```

## Deployment Environment

- Cloud Provider: AWS EC2
- Operating System: Ubuntu 24.04 LTS
- Reverse Proxy: Nginx
- Application Server: Gunicorn
- Backend Framework: Flask
- Machine Learning: Scikit-learn
- CI/CD Security: GitHub Actions

## Scope and Limitations

This is an educational demonstration platform.

- Anti-cheat detection uses sample player behavior.
- Asset ownership uses a local registry, not a live blockchain.
- Biometric protection demonstrates secure data handling rather than live VR sensors.
- Infrastructure protection demonstrates application-level security controls, not comprehensive DDoS mitigation.
- Moderation processes text or supplied transcripts, not live microphone audio.
- DevSecOps demonstrates automated security checks.