# API Spec: Chat Endpoint

> Real-time conversational interface for AI-powered todo management

## Endpoint Overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a message and receive AI response |
| GET | `/api/chat/history` | Retrieve conversation history |
| DELETE | `/api/chat/history` | Clear conversation history |

## POST /api/chat

Send a user message to the AI agent and receive a response.

### Request

```http
POST /api/chat HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

```json
{
  "message": "Add buy groceries to my tasks",
  "conversation_id": "conv_abc123"  // Optional, for continuing conversation
}
```

### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's natural language input |
| `conversation_id` | string | No | ID to continue existing conversation |

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "response": "✅ Added task: \"buy groceries\"\n\nYou now have 3 tasks (2 pending, 1 completed).",
  "conversation_id": "conv_abc123",
  "actions_taken": [
    {
      "tool": "add_task",
      "input": {"title": "buy groceries"},
      "result": {"id": "task_xyz", "title": "buy groceries", "completed": false}
    }
  ],
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens_used": 156,
    "processing_time_ms": 1234
  }
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI-generated response text |
| `conversation_id` | string | Conversation ID for context continuity |
| `actions_taken` | array | List of MCP tools invoked |
| `metadata` | object | Processing information |

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Message is required",
  "error_code": "INVALID_REQUEST"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token",
  "error_code": "UNAUTHORIZED"
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "error_code": "RATE_LIMITED",
  "retry_after": 60
}
```

#### 500 Internal Server Error
```json
{
  "detail": "AI service temporarily unavailable",
  "error_code": "AI_SERVICE_ERROR"
}
```

---

## GET /api/chat/history

Retrieve conversation history for the authenticated user.

### Request

```http
GET /api/chat/history?conversation_id=conv_abc123&limit=50 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

### Query Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `conversation_id` | string | - | Filter by specific conversation |
| `limit` | int | 50 | Max messages to return |
| `offset` | int | 0 | Pagination offset |

### Response

```json
{
  "conversations": [
    {
      "id": "conv_abc123",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:35:00Z",
      "message_count": 5
    }
  ],
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Add buy groceries",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "✅ Added task: \"buy groceries\"",
      "created_at": "2025-01-15T10:30:01Z",
      "actions_taken": [{"tool": "add_task", "...": "..."}]
    }
  ],
  "total": 5,
  "has_more": false
}
```

---

## DELETE /api/chat/history

Clear conversation history for the authenticated user.

### Request

```http
DELETE /api/chat/history?conversation_id=conv_abc123 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

### Query Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `conversation_id` | string | No | Delete specific conversation (or all if omitted) |

### Response

```json
{
  "deleted": true,
  "conversations_deleted": 1,
  "messages_deleted": 5
}
```

---

## Streaming Response (Optional)

For real-time responses, the endpoint supports Server-Sent Events (SSE).

### Request

```http
POST /api/chat HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
Accept: text/event-stream
Content-Type: application/json

{"message": "List my tasks", "stream": true}
```

### Response Stream

```
event: message
data: {"type": "thinking", "content": "Looking up your tasks..."}

event: tool_call
data: {"type": "tool_call", "tool": "list_tasks", "input": {}}

event: tool_result
data: {"type": "tool_result", "tool": "list_tasks", "result": [...]}

event: message
data: {"type": "response", "content": "📋 Your tasks:\n1. [ ] Buy groceries\n..."}

event: done
data: {"type": "done", "conversation_id": "conv_abc123"}
```

---

## Rate Limiting

| Tier | Requests/min | Tokens/day |
|------|--------------|------------|
| Free | 10 | 10,000 |
| Basic | 60 | 100,000 |
| Pro | 300 | 1,000,000 |

---

## Security Considerations

1. **Authentication Required**: All endpoints require valid JWT
2. **User Isolation**: Users can only access their own conversations
3. **Input Sanitization**: All messages sanitized before processing
4. **Token Validation**: JWT verified on every request
5. **Rate Limiting**: Prevents abuse and controls costs

---

## Example Conversations

### Creating Multiple Tasks

```
User: "Add these tasks: buy milk, call dentist, review PR"