# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Referencing Specs with @specs/

Use the `@specs/` pattern to reference specification files in conversations and code:

```
@specs/todo-app/spec.md      # Main feature specification
@specs/todo-app/plan.md      # Implementation plan
@specs/todo-app/tasks.md     # Development tasks

@specs/features/             # Feature-specific specs
@specs/api/                  # API documentation
@specs/database/             # Database schemas
@specs/ui/                   # UI/UX specifications
@specs/overview.md           # Project overview
@specs/architecture.md       # System architecture
```

When implementing features, always check the relevant spec first:
1. Read `@specs/<feature>/spec.md` for requirements
2. Follow `@specs/<feature>/plan.md` for architecture decisions
3. Track progress in `@specs/<feature>/tasks.md`

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

---

## Phase 2 Learnings & Project-Specific Guidelines

### Tech Stack Summary

| Layer | Technology | Key Files |
|-------|------------|-----------|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind | `frontend/src/` |
| Backend | FastAPI + SQLModel | `backend/app/` |
| Database | Neon PostgreSQL (serverless) | `backend/app/database.py` |
| Auth | Better Auth (frontend) + JWT verification (backend) | `frontend/src/lib/auth.ts`, `backend/app/dependencies/auth.py` |

### Authentication Flow

```
User → Better Auth (frontend) → JWT token → Authorization header → FastAPI verification → user_id from 'sub' claim
```

**Critical:** `BETTER_AUTH_SECRET` must be identical in both services.

### Key Implementation Patterns

1. **JWT Verification** (backend) - Uses PyJWT with JWKS for EdDSA
   ```python
   # backend/app/dependencies/auth.py
   import jwt
   from jwt import PyJWKClient

   jwks_client = PyJWKClient(f"{settings.AUTH_URL}/api/auth/jwks")
   signing_key = jwks_client.get_signing_key_from_jwt(token)
   payload = jwt.decode(token, signing_key.key, algorithms=["EdDSA"])
   user_id = payload.get("sub")
   ```

2. **API Client with Auth** (frontend)
   ```typescript
   // frontend/src/lib/api.ts
   headers["Authorization"] = `Bearer ${this.token}`;
   ```

3. **User Ownership Enforcement**
   - Always filter queries by `user_id` from JWT (never from client)
   - Return 403 Forbidden if user tries to access another user's data

4. **Neon Serverless Stability**
   ```python
   engine = create_engine(DATABASE_URL, pool_pre_ping=True)
   ```

### Development Commands

```bash
# Local development
cd frontend && npm run dev     # Port 3000
cd backend && uvicorn app.main:app --reload  # Port 8000

# Docker
docker-compose up --build
docker-compose --profile local-db up  # With local PostgreSQL

# Testing
cd backend && pytest
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| JWT verification fails | Ensure BETTER_AUTH_SECRET is identical in both .env files |
| `JWKError: Unable to find algorithm` | Use `PyJWT` + `PyNaCl` instead of `python-jose` (EdDSA support) |
| Neon connection drops | Use `pool_pre_ping=True` in SQLAlchemy engine |
| CORS errors | Backend CORS allows `http://localhost:3000` |
| 401 on API calls | Check token is being attached via `api.setToken()` |
| 403 on task operations | Verify user_id ownership in backend |
| Node version issues | Better Auth CLI needs Node 20+; use `nvm use 20` |

### Spec References

- `@specs/features/authentication.md` - Auth flow details
- `@specs/features/task-crud.md` - Task CRUD user stories
- `@specs/api/rest-endpoints.md` - API contracts
- `@specs/database/schema.md` - Database schema
- `@specs/phase2-architecture-plan.md` - Full Phase 2 architecture

---

## Phase 3 Learnings: AI Chatbot & Real-time Updates

### Tech Stack Additions

| Layer | Technology | Key Files |
|-------|------------|-----------|
| AI Chat | Claude/OpenAI + MCP Tools | `backend/app/agent/`, `backend/app/mcp/` |
| Event System | Custom EventEmitter | `frontend/src/lib/task-events.ts` |
| Notifications | TaskNotification component | `frontend/src/components/TaskNotification.tsx` |

### Task Event System

Real-time communication between ChatWidget and Dashboard when tasks are modified via AI chatbot.

```typescript
// frontend/src/lib/task-events.ts
type TaskEventType = 'added' | 'completed' | 'updated' | 'deleted';

// Emitting events (ChatWidget)
taskEvents.taskAdded(taskId, taskTitle);
taskEvents.taskCompleted(taskId, taskTitle);
taskEvents.taskUpdated(taskId, taskTitle);
taskEvents.taskDeleted(taskId, taskTitle);

// Subscribing to events (Dashboard)
useEffect(() => {
  const unsubscribe = taskEvents.subscribe((event: TaskEvent) => {
    // Create notification, refresh task list
  });
  return () => unsubscribe();
}, []);
```

### Chat API Response Types

```typescript
// frontend/src/lib/chat-api.ts
interface TaskResult {
  id: string;
  title: string;
  completed?: boolean;
}

interface ActionResult {
  success: boolean;
  task?: TaskResult;
  tasks?: TaskResult[];
  deleted?: TaskResult[];
  message?: string;
}

interface ActionTaken {
  tool: string;
  input: Record<string, unknown>;
  result: ActionResult;
}
```

### Notification Component

Color-coded pill badges with fade-away animation:
- Green (`added`) - New task created
- Blue (`completed`) - Task marked complete
- Yellow (`updated`) - Task modified
- Red (`deleted`) - Task removed

```typescript
// Usage in TaskItem
{notification && (
  <TaskNotification
    message={notification.message}
    type={notification.type}
  />
)}
```

### Tailwind Animation Config

```typescript
// frontend/tailwind.config.ts
theme: {
  extend: {
    keyframes: {
      'slide-in': {
        '0%': { opacity: '0', transform: 'translateX(-10px)' },
        '100%': { opacity: '1', transform: 'translateX(0)' },
      },
    },
    animation: {
      'slide-in': 'slide-in 0.3s ease-out',
    },
  },
}
```

### Chat API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/chat` | Yes | Send chat message to AI agent |
| GET | `/api/chat/history` | Yes | Get conversation history |
| DELETE | `/api/chat/history` | Yes | Clear conversation history |

### Key Files - Phase 3

| File | Purpose |
|------|---------|
| `frontend/src/lib/task-events.ts` | Event emitter singleton |
| `frontend/src/lib/chat-api.ts` | Chat API client with types |
| `frontend/src/components/Chat/ChatWidget.tsx` | Chat UI with event emission |
| `frontend/src/components/TaskNotification.tsx` | Notification pill component |
| `frontend/src/components/TaskItem.tsx` | Task item with notification |
| `backend/app/routers/chat.py` | Chat API endpoint |
| `backend/app/agent/` | AI agent implementation |
| `backend/app/mcp/` | MCP tools for task operations |

---

## Local Session Memory

For session-specific context, status, and notes, see `CLAUDE.local.md` (git-ignored).
This file contains:
- Current project status
- Quick start commands
- Session history and debugging notes
- Test credentials and commands

## Active Technologies
- TypeScript 5.x (frontend), Python 3.11+ (backend) (001-divi-voice-chatbot)
- N/A (voice data is ephemeral, not stored) (001-divi-voice-chatbot)

## Recent Changes
- 001-divi-voice-chatbot: Added TypeScript 5.x (frontend), Python 3.11+ (backend)
