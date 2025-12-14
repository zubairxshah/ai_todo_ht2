# Feature: User Authentication

**Status:** Active
**Phase:** phase2-web
**Priority:** P1

## User Stories

### US-1: Sign Up
**As a** visitor
**I can** sign up with email/password
**So that** I can create an account and use the app

**Acceptance Criteria:**
- [ ] Registration form with email and password fields
- [ ] Password validation (minimum length)
- [ ] Email uniqueness check
- [ ] Successful registration logs user in automatically
- [ ] Error messages for invalid input

### US-2: Sign In
**As a** visitor
**I can** sign in with my credentials
**So that** I can access my tasks

**Acceptance Criteria:**
- [ ] Login form with email and password fields
- [ ] Successful login redirects to dashboard
- [ ] Invalid credentials show error message
- [ ] JWT token stored for subsequent requests

### US-3: Persistent Sessions
**As a** user
**I stay** logged in across sessions
**So that** I don't have to sign in every time

**Acceptance Criteria:**
- [ ] Session persists across browser refresh
- [ ] Session persists across browser close/reopen
- [ ] Token refresh handled automatically
- [ ] Logout clears session completely

### US-4: Protected Routes
**As a** system requirement
**Only** authenticated users can access tasks
**So that** user data remains private

**Acceptance Criteria:**
- [ ] Unauthenticated users redirected to login
- [ ] Dashboard only accessible with valid session
- [ ] API calls without token return 401
- [ ] Expired tokens trigger re-authentication

## Technical Implementation

### Frontend (Next.js + Better Auth)

```
┌─────────────────────────────────────────────────┐
│                   Next.js App                    │
├─────────────────────────────────────────────────┤
│  Better Auth Client                              │
│  ├── JWT Plugin enabled                          │
│  ├── Session management                          │
│  └── Token storage (httpOnly cookie)             │
├─────────────────────────────────────────────────┤
│  API Client (src/lib/api.ts)                     │
│  └── Attaches: Authorization: Bearer <token>     │
└─────────────────────────────────────────────────┘
```

### Backend (FastAPI + JWT Verification)

```
┌─────────────────────────────────────────────────┐
│                   FastAPI                        │
├─────────────────────────────────────────────────┤
│  Auth Dependency (app/dependencies/auth.py)      │
│  ├── Extracts token from Authorization header    │
│  ├── Verifies JWT with BETTER_AUTH_SECRET        │
│  └── Returns user_id from token 'sub' claim      │
├─────────────────────────────────────────────────┤
│  Protected Routes                                │
│  └── All /api/tasks/* use get_current_user_id   │
└─────────────────────────────────────────────────┘
```

### Authentication Flow

```
1. User submits credentials (login/register)
          │
          ▼
2. Better Auth validates & creates session
          │
          ▼
3. JWT signed with BETTER_AUTH_SECRET
          │
          ▼
4. Token stored in httpOnly cookie
          │
          ▼
5. Frontend API client reads token
          │
          ▼
6. Request sent with Authorization: Bearer <token>
          │
          ▼
7. FastAPI extracts & verifies JWT
          │
          ▼
8. user_id extracted from 'sub' claim
          │
          ▼
9. All task queries filtered by user_id
```

### Shared Secret

```bash
# MUST be identical in both services
# frontend/.env.local
BETTER_AUTH_SECRET=your-secret-key-here

# backend/.env
BETTER_AUTH_SECRET=your-secret-key-here
```

## Security Requirements

- JWT signed with HS256 algorithm
- Tokens verified on every protected request
- user_id NEVER provided by client - always from token
- Failed verification returns 401 Unauthorized
- No sensitive data stored in JWT payload

## Key Files

| File | Purpose |
|------|---------|
| `frontend/src/lib/auth.ts` | Better Auth configuration |
| `frontend/src/lib/api.ts` | API client with auth header |
| `backend/app/dependencies/auth.py` | JWT verification |
| `backend/app/config.py` | BETTER_AUTH_SECRET loading |

## Test Scenarios

1. **Register:** New user signs up → redirected to dashboard
2. **Login:** Existing user signs in → sees their tasks
3. **Persist:** Close browser, reopen → still logged in
4. **Protect:** Access /dashboard without auth → redirect to login
5. **API Guard:** Call /api/tasks without token → 401 response
6. **Isolation:** User A's token cannot access User B's tasks
