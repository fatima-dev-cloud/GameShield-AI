
# GameShield AI — DevSecOps CI/CD Workflow

## Overview

GameShield AI uses GitHub Actions to automate security checks during development.

## Workflow Diagram

```mermaid
flowchart TD
    A["Developer - Windows VS Code"]
    B["Git Commit and Push"]
    C["GitHub Repository"]
    D["GitHub Actions - security.yml"]
    E["Install Python Dependencies"]
    F["Run Automated Tests"]
    G["Run Security Checks"]
    H{"Workflow Result"}
    I["Checks Passed"]
    J["Investigate and Fix Failures"]
    K["AWS EC2 Deployment - Separate Step"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> H
    H -->|"Pass"| I
    H -->|"Fail"| J
    J --> A
    I -.->|"Manual Deployment Process"| K
```

## Development Workflow

1. Developer modifies the project in VS Code.
2. Git commits are pushed to GitHub.
3. GitHub Actions starts the configured security workflow.
4. Automated tests and security checks execute.
5. Results are displayed in the GitHub Actions interface.
6. Failed checks are investigated and corrected.
7. Deployment to AWS EC2 is handled separately.

## Tools

- Git and GitHub
- GitHub Actions
- Python
- Pytest
- Bandit
- Dependency security auditing
- AWS EC2
- Nginx
- Gunicorn

## Important Clarification

This workflow documents automated CI security checks.

It does not claim that GitHub Actions automatically deploys code to AWS EC2. Deployment is a separate process.