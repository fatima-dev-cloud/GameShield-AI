# GameShield AI — Voice Moderation Setup

## 1. Install Dependencies

From the repository root:

```bash
python -m pip install -r requirements-dev.txt
```

The project requires `vosk==0.3.45`.

## 2. Download the Vosk Speech Recognition Model

Download the English model:

**Model:** `vosk-model-small-en-us-0.15`

**Official model directory:** https://alphacephei.com/vosk/models

Extract the model into:

```text
models/vosk/vosk-model-small-en-us-0.15/
```

Verify that the following file exists:

```text
models/vosk/vosk-model-small-en-us-0.15/am/final.mdl
```

The speech recognition model is stored locally and is not committed to GitHub.

## 3. Configure the Model Path

On Ubuntu, from the repository root:

```bash
export VOSK_MODEL_PATH="$PWD/models/vosk/vosk-model-small-en-us-0.15"
```

This environment variable must be configured for the process running the application.

## 4. Supported Audio Format

The voice moderation pipeline accepts:

- Uncompressed WAV audio
- Mono channel
- 16-bit PCM
- Maximum file size: 10 MB

## 5. Voice Moderation API

**Endpoint:** `POST /api/moderation/voice`

**Upload field:** `audio`

Processing pipeline:

```text
WAV Upload
    |
    v
Audio Validation
    |
    v
Vosk Speech Recognition
    |
    v
Text Moderation
    |
    v
JSON Moderation Decision
```

## 6. Local Verification

A synthetic WAV file can be generated on Ubuntu using:

```bash
mkdir -p /tmp/gameshield-voice-test

espeak-ng -v en-us -s 125 \
  -w /tmp/gameshield-voice-test/safe_voice.wav \
  "Hello team. This is a safe gaming voice chat message."
```

The generated WAV can be used for local transcription and API verification.

## 7. Verified Development Results

On 29 October 2026, the Ubuntu development environment successfully demonstrated:

- Vosk model initialization.
- Real synthetic-WAV speech transcription.
- Voice moderation using the actual transcription.
- Flask test-client WAV upload.
- HTTP 200 API response.
- Safe-content classification with `ALLOW` action.

The speech recognition output contained minor inaccuracies.

## 8. Limitations

- Voice processing currently uses prerecorded WAV uploads.
- Live audio streaming is not implemented.
- Synthetic speech recognition accuracy is not guaranteed.
- Flask test-client verification does not establish production deployment.
- The Vosk model must be downloaded separately in a fresh environment.
- Clean-environment reproducibility and a fresh CI run require separate verification.