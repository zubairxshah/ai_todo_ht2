# Data Model: Divi Voice Chatbot

**Feature**: 001-divi-voice-chatbot
**Date**: 2025-12-21

## Overview

Voice data is ephemeral - not persisted to database. These models represent in-memory state during voice interactions.

---

## Frontend Types (TypeScript)

### VoiceState

Represents the current state of voice input.

```typescript
type VoiceStatus = 'idle' | 'listening' | 'processing' | 'error';

interface VoiceState {
  status: VoiceStatus;
  isSupported: boolean;           // Web Speech API available
  permissionState: 'granted' | 'denied' | 'prompt' | 'unknown';
  transcription: string | null;   // Current/last transcription
  confidence: number | null;      // 0-1 confidence score
  error: VoiceError | null;       // Last error if any
}
```

### VoiceError

Represents voice-related errors.

```typescript
type VoiceErrorCode =
  | 'permission_denied'      // User denied microphone access
  | 'not_supported'          // Browser doesn't support speech recognition
  | 'network_error'          // Whisper API call failed
  | 'no_speech'              // No speech detected in audio
  | 'audio_capture_error'    // Failed to capture audio
  | 'transcription_failed'   // Speech recognition returned no result
  | 'aborted';               // User cancelled recording

interface VoiceError {
  code: VoiceErrorCode;
  message: string;
  recoverable: boolean;  // Can user retry?
}
```

### VoiceInputConfig

Configuration for voice input behavior.

```typescript
interface VoiceInputConfig {
  language: string;              // BCP-47 language code, default 'en-US'
  continuous: boolean;           // Keep listening after result, default false
  interimResults: boolean;       // Show partial results, default true
  maxDuration: number;           // Max recording time in ms, default 60000
  silenceTimeout: number;        // Stop after silence in ms, default 3000
}
```

### VoiceInputHookReturn

Return type for useVoiceInput hook.

```typescript
interface VoiceInputHookReturn {
  // State
  state: VoiceState;

  // Actions
  startListening: () => Promise<void>;
  stopListening: () => void;
  cancelListening: () => void;

  // Computed
  isListening: boolean;
  isProcessing: boolean;
  canUseVoice: boolean;
}
```

---

## Backend Types (Python/Pydantic)

### TranscriptionRequest

Request to the fallback transcription endpoint.

```python
from pydantic import BaseModel
from fastapi import UploadFile

# Note: UploadFile used directly in endpoint, not as Pydantic model
# This documents the expected format
class TranscriptionRequestDoc:
    """
    POST /api/transcribe
    Content-Type: multipart/form-data

    Fields:
        audio: UploadFile (required) - Audio file in webm, wav, or mp3 format
        language: str (optional) - BCP-47 language hint, default 'en'
    """
    pass
```

### TranscriptionResponse

Response from transcription endpoint.

```python
from pydantic import BaseModel
from typing import Optional

class TranscriptionResponse(BaseModel):
    text: str                          # Transcribed text
    confidence: Optional[float] = None # Confidence score 0-1 (if available)
    language: str = "en"               # Detected/used language
    duration_ms: Optional[int] = None  # Audio duration in milliseconds

class TranscriptionError(BaseModel):
    error: str                         # Error message
    code: str                          # Error code for client handling
```

---

## State Transitions

### Voice Input State Machine

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
    ┌──────────┐  click mic   ┌───────────┐              │
    │   IDLE   │ ──────────►  │ LISTENING │              │
    └──────────┘              └───────────┘              │
         ▲                         │                     │
         │                         │ speech end /        │
         │                         │ timeout             │
         │                         ▼                     │
         │                   ┌────────────┐              │
         │                   │ PROCESSING │              │
         │                   └────────────┘              │
         │                         │                     │
         │    ┌────────────────────┼────────────────────┐│
         │    │                    │                    ││
         │    ▼                    ▼                    ▼│
    ┌──────────┐            ┌───────────┐         ┌─────┴─┐
    │  ERROR   │            │  SUCCESS  │         │ CANCEL│
    └──────────┘            └───────────┘         └───────┘
         │                         │
         │ retry                   │ auto-submit
         └─────────────────────────┴──────────► IDLE
```

### Transitions

| From | Event | To | Side Effect |
|------|-------|-----|-------------|
| IDLE | click mic (supported) | LISTENING | Request mic permission, start recognition |
| IDLE | click mic (unsupported) | ERROR | Show "not supported" error |
| LISTENING | speech end | PROCESSING | Stop recognition, process result |
| LISTENING | timeout (no speech) | ERROR | Show "no speech" error |
| LISTENING | cancel click | IDLE | Abort recognition |
| PROCESSING | transcription success | IDLE | Submit to chat, clear state |
| PROCESSING | transcription fail | ERROR | Show error message |
| ERROR | retry | IDLE | Clear error |
| ERROR | dismiss | IDLE | Clear error |

---

## Validation Rules

### Audio File (Backend)
- Max size: 25 MB
- Allowed formats: webm, wav, mp3, m4a, ogg
- Min duration: 0.1 seconds
- Max duration: 60 seconds

### Transcription Result
- Min length: 1 character
- Max length: 5000 characters
- Must be valid UTF-8

---

## No Database Schema

Voice data is intentionally not persisted:
- Audio recordings are processed and discarded
- Transcriptions become chat messages (existing Message model)
- No new database tables required

This aligns with privacy-first design and YAGNI principles.
