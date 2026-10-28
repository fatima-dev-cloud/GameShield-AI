# GameShield AI — Kernel-Event Simulation Architecture

## Architecture Diagram

```mermaid
flowchart TD
    subgraph DEVICE["Trust Boundary 1 — Demonstration Player Device"]
        CLIENT["Demonstration Client"]
        GENERATOR["Synthetic Event Generation<br/>Explicit simulation=true"]
        KERNEL["Operating-System Kernel<br/>NOT CONNECTED — NO KERNEL TELEMETRY"]

        CLIENT -->|"Create demonstration input"| GENERATOR
        KERNEL -.->|"Absent integration — no event collection"| GENERATOR
    end

    subgraph NETWORK["Trust Boundary 2 — Network / Reverse Proxy"]
        PROXY["Reverse Proxy / Network Boundary<br/>Transport and forwarding boundary"]
    end

    subgraph SERVER["Trust Boundary 3 — GameShield Server"]
        FLASK["Flask API<br/>POST /api/anti-cheat/kernel-simulation/analyze"]
        LIMITER["Global Rate Limiter"]
        FEATURE["Feature-Switch Verification<br/>Disabled by default"]
        AUTH["Bearer-Token Authentication<br/>Configuration supplied"]
        BODY["Raw Request-Body Limit<br/>Checked before JSON parsing"]
        JSON["JSON Object Parsing"]

        subgraph SIMULATION["Educational Kernel-Event Simulation — Implemented in User Space"]
            VALIDATE["Strict Event Validation<br/>Schema, fields, UTC timestamp,<br/>simulation marker and bounded values"]
            CANONICAL["Canonical Event-Size Limit<br/>Maximum 4096 encoded bytes"]
            CLASSIFY["Deterministic Risk Classification<br/>LOW / MEDIUM / HIGH<br/>Score capped at 100"]
            RESULT["Audit-Only Response<br/>simulation=true<br/>kernel_observed=false<br/>enforcement=DISABLED<br/>decision=AUDIT_ONLY"]
        end

        EXISTING["Existing Server-Side Anti-Cheat<br/>Behavior analysis, cheat-type detection,<br/>account sharing, rank boosting and<br/>server-side action validation"]

        FLASK -->|"Apply application request controls"| LIMITER
        LIMITER -->|"Allowed request"| FEATURE
        FEATURE -->|"Endpoint enabled"| AUTH
        AUTH -->|"Authenticated demonstration request"| BODY
        BODY -->|"Body within 8192-byte HTTP limit"| JSON
        JSON -->|"Parsed JSON object"| VALIDATE
        VALIDATE -->|"Validated synthetic event"| CANONICAL
        CANONICAL -->|"Size accepted"| CLASSIFY
        CLASSIFY -->|"Derived score, level and reason code"| RESULT

        FLASK -->|"Separate implemented API paths"| EXISTING
    end

    FUTURE["Future Real Kernel Integration<br/>NOT IMPLEMENTED"]

    GENERATOR -->|"HTTP request with synthetic JSON<br/>and bearer credential"| PROXY
    PROXY -->|"Forwarded request"| FLASK
    RESULT -->|"HTTP JSON response — no enforcement"| PROXY
    PROXY -->|"Return audit result"| CLIENT

    KERNEL -.->|"Possible future trusted telemetry source"| FUTURE
    FUTURE -.->|"Future integration only — absent today"| FLASK
```

## Interpretation

Solid arrows represent the implemented request and response flow. The
demonstration client creates explicitly synthetic events, which cross the
network boundary and are processed by Flask, application security controls,
strict validation and deterministic audit-only classification.

Dashed arrows represent absent or future integration only. The operating-system
kernel is not connected to this pipeline, and the application does not collect
kernel telemetry, load a kernel module, attach eBPF programs or provide kernel
protection. The future integration node is architectural context, not an
implemented capability.

The educational simulation is separate from the existing server-side
anti-cheat functions. Those server-side functions analyze submitted game and
player data, while this pipeline classifies synthetic kernel-like events. A
simulation result is evidence of deterministic application behavior only; it
does not prove cheating, prevent cheating or establish that an event originated
from the operating-system kernel.
