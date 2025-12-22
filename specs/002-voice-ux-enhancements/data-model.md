# Data Model: Voice UX Enhancements

**Feature Branch**: `002-voice-ux-enhancements`
**Created**: 2025-12-22

## Overview

This feature does not introduce new database entities. Changes are limited to frontend state management and static assets.

## Entities

### VoiceCommand (Frontend State Only)

**Description**: Represents a voice input being processed - exists only in component state, not persisted.

| Field | Type | Description |
|-------|------|-------------|
| transcription | string | The recognized speech text |
| confidence | number | Recognition confidence (0-1) |
| timestamp | Date | When recognition completed |
| status | enum | 'idle' \| 'listening' \| 'processing' \| 'error' |

**State Transitions**:
```
idle → listening (user clicks mic)
listening → processing (speech ends)
processing → idle (command submitted)
listening → error (recognition failure)
error → idle (user retry or timeout)
```

**Note**: This entity already exists in `useVoiceInput.ts` as `VoiceState`. No changes needed.

---

### Favicon (Static Asset)

**Description**: Browser tab icon for application branding.

| Property | Value |
|----------|-------|
| Source URL | https://cdn-icons-png.freepik.com/512/17394/17394786.png |
| Local Path | frontend/src/app/icon.png |
| Format | PNG |
| Recommended Size | 512x512 px (Next.js will generate smaller sizes) |

**Additional Files** (optional):
- `frontend/src/app/apple-icon.png` - iOS bookmark icon
- `frontend/src/app/favicon.ico` - Legacy browser support

---

## Database Impact

**None** - This feature does not modify the database schema.

---

## State Management Changes

### ChatKitWidget Component State

**Current State** (unchanged):
```typescript
const [input, setInput] = useState('');       // Text input field value
const [loading, setLoading] = useState(false); // Submission in progress
const [messages, setMessages] = useState<Message[]>([]); // Chat history
```

**Behavioral Change**:
- Voice commands no longer populate `input` state
- `input` remains empty during voice command flow
- Direct submission bypasses input state entirely

### Voice State (from useVoiceInput hook)

**No changes** - Existing state structure is sufficient:
```typescript
interface VoiceState {
  status: 'idle' | 'listening' | 'processing' | 'error';
  isSupported: boolean;
  permissionState: PermissionState | 'unknown';
  transcription: string | null;
  confidence: number | null;
  error: VoiceError | null;
}
```

---

## Validation Rules

| Rule | Scope | Description |
|------|-------|-------------|
| Non-empty transcription | Voice submission | Only submit if transcription.trim() is not empty |
| Valid icon format | Favicon | PNG or ICO format, minimum 16x16 |
| Confidence threshold | Voice (optional) | Could reject low-confidence results (not implemented) |

---

## Relationships

```
VoiceCommand (state) --triggers--> Message (state)
                                        |
                                        v
                                  API Request ---> Backend (unchanged)
```

The voice command flow remains the same as text input - only the trigger mechanism changes.
