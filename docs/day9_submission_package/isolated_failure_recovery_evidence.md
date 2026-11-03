# Isolated Failure and Recovery Evidence

**Execution date:** 2 November 2026
**Environment:** Development EC2, loopback only
**Production accessed:** No

## Deployment configuration

An isolated Gunicorn 23.0.0 process was started from the development checkout
with one worker bound only to `127.0.0.1:18765`. The process used the existing
development virtual environment and explicit `PYTHONPATH` and
`VOSK_MODEL_PATH`. Access and error logs were directed to `/tmp`.

## Initial health results

| Request | Status | Time |
|---|---:|---:|
| `GET /` | 200 | 0.001975 s |
| `GET /dashboard` | 200 | 0.015321 s |
| `GET /static/dashboard.css` | 200 | 0.004489 s |
| `GET /static/dashboard.js` | 200 | 0.001337 s |
| `GET /api/status` | 200 | 0.001222 s |
| `GET /api/devsecops/report` | 200 | 0.001184 s |

## Controlled failure

Only the isolated Gunicorn session started for this test was terminated. A
subsequent request to `GET /api/status` failed to connect within the bounded
timeout, confirming that the isolated endpoint was unavailable:

```text
FAILURE_SIMULATION_PASS_ENDPOINT_UNAVAILABLE
```

No system or production service was stopped or restarted.

## Recovery results

The same loopback-only Gunicorn configuration was started again.

| Request | Status | Time |
|---|---:|---:|
| `GET /` | 200 | 0.002017 s |
| `GET /dashboard` | 200 | 0.015239 s |
| `GET /static/dashboard.css` | 200 | 0.004684 s |
| `GET /static/dashboard.js` | 200 | 0.001345 s |
| `GET /api/status` | 200 | 0.000920 s |
| `GET /api/devsecops/report` | 200 | 0.001140 s |

Git reported no tracked or untracked repository changes after recovery:

```text
TRACKED_AND_WORKTREE_INTEGRITY_PASS
```

The recovered isolated process was then stopped successfully.

## Result and boundary

**ISOLATED APPLICATION FAILURE/RECOVERY: PASS.** This verifies local process
restart and application availability only. It does not demonstrate systemd,
Nginx, production, EC2 instance, volume, AMI, snapshot, DNS, certificate or
AWS disaster recovery. Those external capabilities remain unverified.
