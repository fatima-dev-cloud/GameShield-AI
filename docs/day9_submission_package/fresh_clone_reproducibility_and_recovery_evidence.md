# Fresh-Clone Reproducibility and Isolated Recovery Evidence

**Date:** 2 November 2026
**Source:** `origin/development` at `e5e11ebb98794d92916820145547617f8c38f1b6`
**Environment:** disposable `/tmp` clone and new Python 3 virtual environment
**Production/AWS access:** none

## Reproducibility result

A genuinely fresh GitHub clone used a new virtual environment and installed `requirements-dev.txt` without reusing the repository environment. `pip check` passed. Both ignored demonstration models were regenerated from the tracked synthetic datasets: anti-cheat used 30 records and scored 100% on its deterministic nine-record split; moderation used 30 messages and scored 77.78% on its deterministic nine-message split. These small synthetic results are not production benchmarks. The fresh environment passed **269 tests in 4.65 seconds**.

## Vosk verification

The official archive `https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip` had SHA256 `30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498`. ZIP integrity passed. All 14 extracted files matched the configured development model by relative path and SHA256. The archive/model remain external ignored resources.

## Isolated failure and recovery

Gunicorn 23.0.0 started from the fresh environment on loopback-only `127.0.0.1:18767` with `PYTHONPATH=src` and the fresh `VOSK_MODEL_PATH`. `/api/status` returned HTTP 200. After controlled stop, curl returned exit 7 and HTTP `000`. After restart, `/api/status` returned HTTP 200 again. The process was stopped.

The clone had no tracked modifications; its only visible untracked item was the downloaded Vosk ZIP. The disposable clone was removed after evidence capture.

## Boundary

This proves clean-clone installation and application-process restart in development. It does **not** prove EC2, EBS, AMI, networking, certificate, production-data or AWS disaster recovery. Task 9.3 remains PARTIAL.
