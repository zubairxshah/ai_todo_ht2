<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0 (Initial ratification)

Modified principles: N/A (Initial creation)

Added sections:
  - I. Test-First Development (TDD)
  - II. Simplicity & YAGNI
  - III. Security-First
  - IV. Type Safety
  - Technology Standards
  - Development Workflow
  - Governance

Removed sections: N/A (Initial creation)

Templates validated:
  ✅ .specify/templates/plan-template.md - Constitution Check section present
  ✅ .specify/templates/spec-template.md - Requirements structure compatible
  ✅ .specify/templates/tasks-template.md - Test-first workflow aligned

Follow-up TODOs: None
-->

# Todo P1 Constitution

## Core Principles

### I. Test-First Development (TDD)

Test-Driven Development is **NON-NEGOTIABLE** for this project.

- Tests MUST be written before implementation code
- Tests MUST fail before writing implementation (Red phase)
- Implementation MUST make tests pass with minimal code (Green phase)
- Code MUST be refactored only after tests pass (Refactor phase)
- No feature is considered complete without passing tests

**Rationale**: TDD ensures correctness by design, prevents regression, and produces
maintainable code with clear specifications embedded in tests.

### II. Simplicity & YAGNI

Keep implementations as simple as possible. You Aren't Gonna Need It.

- Code MUST solve only the current requirement, not hypothetical future needs
- Abstractions MUST NOT be introduced until there are at least three concrete use cases
- Dependencies MUST be justified; prefer standard library over third-party packages
- Every line of code MUST have a clear, immediate purpose

**Rationale**: Premature abstraction and over-engineering create maintenance burden,
obscure intent, and slow development without delivering value.

### III. Security-First

Security is a foundational requirement, not an afterthought.

- All user input MUST be validated and sanitized at system boundaries
- Authentication and authorization MUST be enforced on all protected resources
- Secrets and credentials MUST NEVER be hardcoded; use environment variables
- User ownership MUST be enforced on all task operations
- OWASP Top 10 vulnerabilities MUST be actively prevented

**Rationale**: Security breaches are costly and damage trust. Building security in from
the start is far cheaper than retrofitting it later.

### IV. Type Safety

Strong typing prevents entire categories of bugs at compile time.

- TypeScript strict mode MUST be enabled for frontend
- Python type hints MUST be used throughout backend code
- Explicit types MUST be used for function parameters and return values
- Runtime validation MUST use Pydantic/SQLModel schemas

**Rationale**: Type safety catches errors before runtime, improves IDE support,
and serves as executable documentation for data shapes and contracts.

## Technology Standards

### Frontend Stack

- **Framework**: Next.js (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Auth Client**: Better Auth client SDK

### Backend Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL
- **Auth**: Better Auth with JWT plugin
- **Shared Secret**: BETTER_AUTH_SECRET (environment variable)

### Environment Variables (Required)

```
# Database
DATABASE_URL=postgresql://...@neon.tech/...

# Authentication
BETTER_AUTH_SECRET=<shared-secret-for-jwt>
BETTER_AUTH_URL=<auth-server-url>

# Frontend
NEXT_PUBLIC_API_URL=<backend-api-url>
```

### Code Quality Gates

- All code MUST pass linting with zero errors
- All tests MUST pass before merge
- Type checking MUST pass with no errors

## Development Workflow

### Branching Strategy

- `main` branch MUST always be deployable
- Feature branches MUST follow naming: `<issue-number>-<brief-description>`
- All changes MUST go through pull requests

### Definition of Done

A task is complete when:
1. Tests are written and passing
2. Code passes all linting and type checks
3. User ownership is enforced for task operations
4. No hardcoded secrets

## Governance

### Amendment Procedure

1. Propose changes via pull request to this constitution
2. Changes MUST include rationale and impact assessment
3. Breaking changes to principles require MAJOR version bump

### Compliance

- All PRs MUST verify compliance with this constitution
- The constitution supersedes all other development practices

**Version**: 1.0.0 | **Ratified**: 2025-12-14 | **Last Amended**: 2025-12-14
