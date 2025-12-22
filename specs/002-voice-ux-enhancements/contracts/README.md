# API Contracts: Voice UX Enhancements

**Feature Branch**: `002-voice-ux-enhancements`
**Created**: 2025-12-22

## Overview

This feature does not introduce new API endpoints or modify existing contracts.

## Existing Endpoints Used

### POST /api/chatkit

**Purpose**: Submit chat message (text or voice transcription)
**Auth**: Bearer JWT token required

**Request**:
```json
{
  "message": "string",
  "thread_id": "string | null"
}
```

**Response**: Server-Sent Events (SSE) stream

**Note**: Voice commands use the same endpoint as text input - no changes needed.

---

## Frontend-Only Changes

This feature modifies only the client-side submission flow:

| Component | Change | Impact on API |
|-----------|--------|---------------|
| ChatKitWidget | Voice bypasses input field | None - same payload |
| handleVoiceTranscription | Direct submit | None - same endpoint |
| Favicon | Static asset | None - no API calls |

---

## Contract Validation

| Aspect | Status |
|--------|--------|
| New endpoints | None required |
| Request changes | None |
| Response changes | None |
| Auth changes | None |

The existing `/api/chatkit` contract is fully sufficient for this feature.
