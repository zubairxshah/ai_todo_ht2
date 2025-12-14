# REST API Endpoints

**Base URL:** `http://localhost:8000`
**Authentication:** JWT Bearer token in Authorization header

## Authentication

All `/api/*` endpoints require authentication:

```
Authorization: Bearer <jwt_token>
```

The `user_id` is extracted from the JWT token's `sub` claim on the backend. Clients never send `user_id` directly - this prevents users from accessing other users' data.

## Endpoints

### Health Check

```
GET /health
```

**Auth Required:** No

**Response:**
```json
{
  "status": "healthy"
}
```

---

### List Tasks

```
GET /api/tasks
```

**Auth Required:** Yes

**Description:** Returns all tasks belonging to the authenticated user.

**Response (200):**
```json
[
  {
    "id": "uuid-string",
    "title": "Buy groceries",
    "completed": false,
    "user_id": "uuid-string",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

**Errors:**
- `401 Unauthorized` - Invalid or missing token

---

### Create Task

```
POST /api/tasks
```

**Auth Required:** Yes

**Request Body:**
```json
{
  "title": "Buy groceries"
}
```

**Response (201):**
```json
{
  "id": "uuid-string",
  "title": "Buy groceries",
  "completed": false,
  "user_id": "uuid-string",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or missing token
- `422 Unprocessable Entity` - Validation error (empty title)

---

### Update Task

```
PATCH /api/tasks/{id}
```

**Auth Required:** Yes

**Path Parameters:**
- `id` - Task UUID

**Request Body (partial update):**
```json
{
  "title": "Buy groceries and milk",
  "completed": true
}
```

**Response (200):**
```json
{
  "id": "uuid-string",
  "title": "Buy groceries and milk",
  "completed": true,
  "user_id": "uuid-string",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Task belongs to another user
- `404 Not Found` - Task does not exist

---

### Delete Task

```
DELETE /api/tasks/{id}
```

**Auth Required:** Yes

**Path Parameters:**
- `id` - Task UUID

**Response (204):** No content

**Errors:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Task belongs to another user
- `404 Not Found` - Task does not exist

---

## Error Response Format

All errors return JSON:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## CORS Configuration

Backend allows requests from:
- `http://localhost:3000` (frontend dev server)

## Rate Limiting

Not implemented in MVP. Consider for production.
