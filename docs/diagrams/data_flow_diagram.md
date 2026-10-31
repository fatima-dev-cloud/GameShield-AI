
# GameShield AI — Data Flow Diagram

## Level 1: Security Analysis Data Flow

```mermaid
flowchart TD
    A["Player / Administrator"]
    B["GameShield AI Dashboard"]
    C["Flask API"]
    D{"Security Module Selection"}
    E["AI Anti-Cheat"]
    F["Virtual Asset Security"]
    G["Identity Security"]
    H["Infrastructure Security"]
    I["Content Moderation"]
    J["DevSecOps Reporting"]
    K["Security Analysis Result"]

    A -->|"Demo Input"| B
    B -->|"HTTPS API Request"| C
    C --> D

    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J

    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K -->|"JSON Response"| C
    C --> B
    B -->|"Display Result"| A
```

## Example: Anti-Cheat Detection

1. Player behavior data is submitted through the dashboard.
2. Flask receives the API request.
3. The anti-cheat module analyzes the submitted behavior.
4. The trained machine learning model generates a prediction.
5. Flask returns the analysis result.
6. The dashboard displays the result.

## Data Protection

- Security analysis uses demonstration data.
- Biometric information should not be exposed in logs.
- Sensitive identity data must be protected.
- The deployed public transport uses HTTPS, but stronger access controls and
  production-hardening evidence are still required.
