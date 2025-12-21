# API Contract: Transcription Endpoint

**Feature**: 001-divi-voice-chatbot
**Date**: 2025-12-21
**Base URL**: `/api`

---

## POST /transcribe

Transcribe audio to text using OpenAI Whisper API. This is a fallback endpoint for browsers that don't support Web Speech API.

### Request

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Body** (multipart/form-data):
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| audio | file | Yes | Audio file (webm, wav, mp3, m4a, ogg) |
| language | string | No | BCP-47 language hint (default: "en") |

**Constraints**:
- Max file size: 25 MB
- Max duration: 60 seconds
- Supported formats: webm, wav, mp3, m4a, ogg

### Response

**Success (200 OK)**:
```json
{
  "text": "add task buy groceries",
  "confidence": 0.95,
  "language": "en",
  "duration_ms": 2340
}
```

| Field | Type | Description |
|-------|------|-------------|
| text | string | Transcribed text |
| confidence | float | Confidence score 0-1 (nullable) |
| language | string | Detected/used language |
| duration_ms | int | Audio duration in milliseconds (nullable) |

**Error Responses**:

**400 Bad Request** - Invalid input:
```json
{
  "error": "No audio file provided",
  "code": "missing_audio"
}
```

```json
{
  "error": "Unsupported audio format. Allowed: webm, wav, mp3, m4a, ogg",
  "code": "invalid_format"
}
```

```json
{
  "error": "Audio file too large. Maximum size: 25MB",
  "code": "file_too_large"
}
```

**401 Unauthorized** - Authentication failed:
```json
{
  "error": "Invalid or missing authentication token",
  "code": "unauthorized"
}
```

**500 Internal Server Error** - Transcription failed:
```json
{
  "error": "Transcription service unavailable",
  "code": "service_error"
}
```

```json
{
  "error": "No speech detected in audio",
  "code": "no_speech"
}
```

### Error Codes

| Code | HTTP Status | Description | Client Action |
|------|-------------|-------------|---------------|
| missing_audio | 400 | No audio file in request | Check form data |
| invalid_format | 400 | Unsupported audio format | Convert to supported format |
| file_too_large | 400 | Audio exceeds 25MB | Record shorter clip |
| unauthorized | 401 | Invalid JWT token | Re-authenticate |
| no_speech | 500 | No speech in audio | Prompt user to speak |
| service_error | 500 | Whisper API failed | Retry or use text input |

### Example

**cURL**:
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -H "Authorization: Bearer eyJ..." \
  -F "audio=@recording.webm" \
  -F "language=en"
```

**TypeScript**:
```typescript
async function transcribeAudio(audioBlob: Blob, token: string): Promise<string> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('language', 'en');

  const response = await fetch('/api/transcribe', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }

  const result = await response.json();
  return result.text;
}
```

---

## Rate Limiting

- **Limit**: 10 requests per minute per user
- **Response**: 429 Too Many Requests
- **Header**: `Retry-After: <seconds>`

---

## Security Considerations

1. **Authentication Required**: All requests must include valid JWT
2. **User Scoping**: Transcriptions are not logged with user data
3. **Audio Not Stored**: Audio files are processed and immediately discarded
4. **Size Limits**: Prevents abuse via large file uploads
5. **Rate Limiting**: Prevents API cost abuse
