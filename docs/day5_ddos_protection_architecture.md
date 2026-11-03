# GameShield AI Day 5 DDoS Protection Architecture

## 1. Purpose

This document records the DDoS and request-integrity controls currently
implemented in GameShield AI and distinguishes them from recommended future
infrastructure controls.

It does not claim that AWS Shield, AWS WAF, Nginx, or any other external
control has been configured or verified. No AWS or production changes are
authorized by this document.

## 2. Scope

Reviewed application components:

- `src/infrastructure_security/rate_limiter.py`
- `src/infrastructure_security/secure_netcode.py`
- `src/app.py`

Out of scope:

- Changing AWS infrastructure
- Changing Security Groups
- Enabling AWS WAF
- Installing or configuring Nginx
- Load testing or stress testing
- Public-IP traffic simulation
- Production EC2 access
- Dashboard changes
- Changes to Day 2–4 modules

## 3. Implemented controls

### 3.1 Application-level rate limiter

`rate_limiter.py` implements an in-memory, per-client sliding-window-style
request limiter.

Current settings:

- Request limit: 10 requests
- Window: 10 seconds
- Temporary block: 30 seconds
- Clock: `time.monotonic()`
- State protection: `threading.Lock`
- Request history: per-client `deque`
- Block state: per-client expiration timestamp

The limiter removes timestamps older than the configured window. When the
client already has 10 timestamps in the active window, the next request is
denied and the client is blocked for 30 seconds.

A triggering denial returns:

- `allowed: false`
- `status: RATE LIMIT EXCEEDED`
- `action: TEMPORARY BLOCK`
- `block_seconds: 30`

Requests during the block return:

- `allowed: false`
- `status: CLIENT TEMPORARILY BLOCKED`
- `remaining_block_seconds`

Allowed requests include the current request count and configured limit.

The trigger is written to:

`logs/infrastructure_security.log`

The log includes the client identifier and block duration.

### 3.2 Flask integration

`src/app.py` invokes `check_rate_limit()` through `@app.before_request`.

Implemented behavior:

- The limiter applies before non-static Flask routes.
- Static-file requests are exempt.
- The client identifier is `request.remote_addr`, falling back to `UNKNOWN`.
- Denied requests return HTTP 429.
- The response identifies the GameShield AI DDoS Protection module.
- Automated tests bypass the limiter when `TESTING` is true unless
  `TEST_RATE_LIMITER` is also true.
- Direct development execution binds Flask to `127.0.0.1:5000`.

The limiter runs before route handlers, so a denied request should not reach
expensive moderation or other application logic.

### 3.3 Secure netcode

`secure_netcode.py` implements packet integrity verification with:

- HMAC-SHA256
- A 32-byte secret generated with `secrets.token_bytes`
- Canonical JSON serialization using sorted keys and compact separators
- Constant-time signature comparison through `hmac.compare_digest`

The local key is stored at:

`config/netcode.key`

Valid and invalid verification attempts are written to the infrastructure
security log. The log records the packet's `player_id` value or `UNKNOWN`;
it does not record the full packet.

The Flask packet-verification route returns HTTP 200 for a valid signature
and HTTP 403 when packet tampering is detected.

## 4. Current limitations

### 4.1 Rate-limiter limitations

The limiter is local process memory only.

Consequences:

- State is lost when the process restarts.
- Multiple worker processes do not share counters.
- Multiple EC2 instances do not share counters.
- A client may receive a separate quota from every worker or instance.
- The dictionaries may retain inactive client keys unless those clients are
  accessed again.
- There is no configured maximum number of tracked client identifiers.
- All non-static routes share one client quota.
- Expensive endpoints do not currently have stricter limits.
- Authenticated user or API-key identity is not part of the limit key.
- The limiter trusts Flask's `request.remote_addr` view of the connection.
- Trusted-proxy behavior is not defined in the reviewed code.

The timestamp-expiry comparison uses `>` rather than `>=`. A request exactly
on the window boundary may retain the oldest timestamp until time advances
past that boundary.

The raw client identifier is written to the infrastructure log. Retention,
access control, and privacy handling for this log must be defined
operationally.

### 4.2 Secure-netcode limitations

The HMAC verifies integrity and possession of the shared key, but the reviewed
packet format does not enforce:

- Nonces
- Sequence numbers
- Packet expiration
- Replay detection
- Per-player keys
- Key rotation
- Centralized key distribution
- File-permission validation
- Shared-key consistency across multiple instances

A correctly signed old packet may therefore be replayed unless another
application component rejects it.

`load_or_create_key()` writes a key automatically when none exists. In a
multi-instance deployment, separate instances could generate different keys.
Production key management should not depend on independently generated local
files.

The player identifier is taken from packet content for logging. It must not
be treated as authenticated identity solely because it appears in the log.

### 4.3 DDoS limitations

An application limiter receives traffic only after the network stack, web
server, and Python process have already accepted it. It cannot independently
protect network bandwidth, connection tables, or host resources from a large
volumetric event.

The existing code is a useful final application layer, not a complete DDoS
defense.

## 5. Proposed layered architecture

The following controls are proposals. They have not been deployed or verified.

### Layer 1: AWS Security Groups

Use Security Groups to expose only required ports.

Proposed posture:

- Permit public HTTPS only through the intended entry point.
- Redirect or avoid public HTTP according to the deployment policy.
- Do not expose the Flask development port publicly.
- Bind the application service to loopback or a private interface.
- Restrict administrative access to approved sources and workflows.
- Remove unused ingress rules.
- Review outbound rules according to application requirements.

Security Groups provide network access control. They do not provide
application request-rate limiting.

### Layer 2: AWS Shield Standard

Confirm through the AWS account and current deployment topology whether the
public entry resource receives AWS Shield Standard protection.

Shield should be treated as infrastructure-level protection. It does not
replace:

- Security Groups
- AWS WAF
- Reverse-proxy limits
- Authentication
- Application rate limits
- Request validation
- Monitoring and incident response

This review did not access AWS and does not claim that Shield coverage was
verified.

### Layer 3: Optional AWS WAF

AWS WAF may be considered if traffic enters through a supported AWS resource,
such as an appropriate load balancer or edge service.

Potential controls:

- AWS-managed baseline rules
- IP reputation rules
- Rate-based rules
- Request-size restrictions
- Method and path restrictions
- Narrow limits for computationally expensive endpoints
- Monitoring or count mode before enforcement
- Logging with approved retention and access controls

WAF rules require false-positive review. Health checks, administrative
traffic, and valid clients must not be blocked accidentally.

This review did not access AWS and does not claim that WAF exists or is
configured.

### Layer 4: Nginx reverse proxy

A future Nginx layer could:

- Listen on the externally exposed application port
- Proxy to Flask on `127.0.0.1`
- Limit requests per client
- Limit concurrent connections
- Apply stricter zones to expensive routes
- Reject oversized bodies
- Configure header, body, and upstream timeouts
- Return HTTP 429 for rate violations
- Reject malformed requests before Flask
- Avoid disclosing internal errors

Forwarded client addresses must be trusted only from known proxy sources.
Arbitrary external forwarding headers must not determine the application
limit key.

Nginx is not currently verified or configured by this work.

### Layer 5: Application-level controls

Retain the existing Flask limiter as a final request-aware control.

Recommended future improvements:

- Define endpoint-specific quotas.
- Apply stricter quotas to CPU-intensive voice processing.
- Use authenticated identity where appropriate.
- Use a shared bounded store for multi-worker deployments.
- Define state expiration and cleanup.
- Bound the number of tracked client keys.
- Preserve monotonic timing.
- Keep limiter decisions ahead of model loading.
- Define trusted-proxy handling explicitly.
- Add standard rate-limit response headers if appropriate.
- Keep HTTP 429 behavior stable.
- Ensure limiter failures do not silently disable protection.

Any shared-store design must be implemented and reviewed separately. This
document does not authorize installation of new services.

### Layer 6: Logging, metrics, and monitoring

Record operational metadata without message, transcript, packet payload, or
authentication-secret contents.

Recommended measurements:

- Requests per route
- HTTP 429 count and rate
- HTTP 403, 408, 413, and 5xx rates
- Active and rejected connections
- Request and response latency
- Request-body size
- CPU and memory consumption
- Moderation and transcription latency
- Reverse-proxy upstream failures
- WAF matches if WAF is later enabled

Recommended log fields:

- UTC timestamp
- Route identifier
- Response status
- Enforcement layer
- Rate-limit decision
- Request duration
- Request size
- Protected or anonymized client identifier
- Non-sensitive error category

Define log retention, access control, alert thresholds, and an incident
runbook before production use.

## 6. Controlled validation strategy

### Deterministic unit tests

The primary validation method is isolated pytest coverage with:

- Mocked monotonic time
- Mocked log writes
- Cleared in-memory limiter state
- Flask's test client
- Explicit test client addresses
- No sleep calls
- No model loading
- No network traffic

Required behaviors:

- First 10 requests are allowed.
- The 11th request is denied.
- The triggering client is blocked for 30 seconds.
- A blocked client remains denied before expiration.
- Access resumes after block expiration.
- Separate clients have separate histories.
- A denied Flask request returns HTTP 429.
- A denied request does not reach its route handler.
- Normal automated tests retain the existing limiter bypass.

### Localhost traffic probe decision

No live localhost probe is proposed for Day 5.

Although the development server binds to `127.0.0.1`, the current limiter:

- Uses shared process-global state
- Writes a log when the limit is triggered
- Applies one quota across all non-static routes
- Has no administrative state-reset endpoint
- Would require starting a live Flask process
- Provides no benefit over deterministic Flask test-client coverage for the
  required behavior

The deterministic tests are safer, faster, repeatable, and produce no public
traffic. No public-IP simulation, flooding, concurrency, or stress testing is
approved.

## 7. Recommended future review items

Before production deployment:

1. Confirm the actual AWS traffic path.
2. Confirm Security Group ingress and egress rules.
3. Confirm whether Shield applies to the public entry resource.
4. Decide whether a WAF-capable entry point is required.
5. Review reverse-proxy limits and trusted proxy settings.
6. Replace per-process limiter state if multiple workers are used.
7. Define endpoint-specific quotas from measured capacity.
8. Add replay protection to signed game packets.
9. Move production secrets to an approved secret-management workflow.
10. Define monitoring, alerting, retention, and incident response.