# Research: Divi Voice Chatbot

**Feature**: 001-divi-voice-chatbot
**Date**: 2025-12-21

## Research Topics

### 1. Web Speech API Browser Support

**Decision**: Use Web Speech API as primary speech recognition method

**Findings**:
- **Chrome**: Full support (SpeechRecognition)
- **Edge**: Full support (uses same engine as Chrome)
- **Safari**: Partial support (requires webkit prefix: webkitSpeechRecognition)
- **Firefox**: Limited support (may require flags, not fully stable)

**Implementation**:
```typescript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const isSupported = typeof SpeechRecognition !== 'undefined';
```

**Rationale**: Covers 85%+ of users (Chrome + Edge + Safari). Firefox users fall back to Whisper API.

**Alternatives Considered**:
- Google Cloud Speech-to-Text: Better accuracy but requires API key, has cost
- Azure Speech Services: Enterprise-grade but overkill for task commands
- Whisper API only: More consistent but every request has latency and cost

---

### 2. Whisper API Integration (Fallback)

**Decision**: Use OpenAI Whisper API for browsers without Web Speech API support

**Findings**:
- Model: `whisper-1` (latest stable)
- Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
- Max file size: 25 MB
- Cost: $0.006 per minute of audio
- Latency: ~1-3 seconds for short clips

**Implementation**:
```python
from openai import OpenAI

client = OpenAI()
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="json"
)
```

**Rationale**: Already using OpenAI for chat, consistent API, excellent accuracy.

**Alternatives Considered**:
- Self-hosted Whisper: Free but requires GPU, complex deployment
- AssemblyAI: Good accuracy but another vendor dependency
- Deepgram: Fast but less accurate for short commands

---

### 3. Audio Recording in Browser

**Decision**: Use MediaRecorder API for capturing audio when Web Speech API unavailable

**Findings**:
- MediaRecorder API has broad support (all modern browsers)
- Preferred format: webm/opus (smaller files, good quality)
- Fallback format: audio/wav (universal compatibility)

**Implementation**:
```typescript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
const chunks: Blob[] = [];
mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
mediaRecorder.onstop = () => {
  const audioBlob = new Blob(chunks, { type: 'audio/webm' });
  // Send to Whisper API
};
```

**Rationale**: Standard API, works in all browsers, compatible with Whisper.

---

### 4. Visual Feedback Patterns

**Decision**: Animated microphone icon with state-based colors and pulsing animation

**Findings**:
- Common patterns: Pulsing circle, waveform visualization, simple icon states
- Accessibility: Color alone insufficient, need icon changes + text labels
- States needed: idle, listening, processing, error

**Implementation**:
```
State       | Icon              | Color   | Animation
------------|-------------------|---------|------------------
idle        | Microphone        | Gray    | None
listening   | Microphone + wave | Blue    | Pulse animation
processing  | Spinner           | Blue    | Rotation
error       | Microphone + X    | Red     | Shake animation
```

**Rationale**: Simple, clear, accessible. Matches existing Tailwind styling.

---

### 5. Microphone Permissions

**Decision**: Request permission on first voice button click, not on page load

**Findings**:
- Browsers block auto-permission requests
- Must be triggered by user gesture (click)
- Permission persists until revoked
- Can detect permission state via Permissions API

**Implementation**:
```typescript
async function checkMicPermission(): Promise<'granted' | 'denied' | 'prompt'> {
  const result = await navigator.permissions.query({ name: 'microphone' as PermissionName });
  return result.state;
}
```

**Rationale**: Follows browser best practices, less intrusive UX.

---

### 6. Integration with Existing ChatKitWidget

**Decision**: Add voice input as parallel input method alongside text input

**Findings**:
- ChatKitWidget has `input` state and `handleSubmit` function
- Can reuse existing message submission flow
- Voice transcription becomes the "input" before submission

**Integration Point**:
```typescript
// In ChatKitWidget, after voice transcription:
setInput(transcribedText);
handleSubmit(new Event('submit')); // Trigger existing flow
```

**Rationale**: Minimal changes to existing code, reuses proven message handling.

---

## Summary

| Topic | Decision | Risk Level |
|-------|----------|------------|
| Primary STT | Web Speech API | Low (well-supported) |
| Fallback STT | OpenAI Whisper API | Low (already integrated) |
| Audio capture | MediaRecorder API | Low (standard API) |
| Visual feedback | State-based icons + animations | Low (CSS only) |
| Permissions | On-demand request | Low (browser standard) |
| Integration | Extend ChatKitWidget | Low (minimal changes) |

**All research topics resolved. Ready for Phase 1 design.**
