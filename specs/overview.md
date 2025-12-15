# Todo P1 - Project Overview

## Purpose

A full-stack Todo application that allows users to manage their personal tasks with secure authentication and data isolation. **Phase III** adds an AI-powered chatbot interface for natural language task management.

## Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend Framework | Next.js (App Router) | 14.x |
| Frontend Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.4.x |
| Authentication | Better Auth | 1.x |
| Backend Framework | FastAPI | 0.109+ |
| ORM | SQLModel | 0.0.14+ |
| Database | Neon PostgreSQL | - |
| Auth Verification | JWT (PyJWT + PyNaCl) | 2.8+ |
| AI/LLM | OpenAI Agents SDK | 0.6+ |
| MCP Protocol | MCP SDK | 1.0+ |
| Chat UI | OpenAI ChatKit | latest |

## Core Features

### Phase I & II: Foundation (Complete)

1. **User Authentication**
   - Registration with email/password
   - Login/logout functionality
   - JWT-based session management (EdDSA)
   - Shared secret between frontend and backend

2. **Task Management**
   - Create new tasks
   - View personal task list
   - Mark tasks as complete/incomplete
   - Edit task titles (inline editing)
   - Delete tasks

3. **Security**
   - User data isolation (users only see their own tasks)
   - All secrets loaded from environment variables
   - CORS configured for frontend origin only

### Phase III: AI Chatbot (Complete)

4. **Natural Language Interface**
   - Add tasks via conversation ("Add buy groceries")
   - List tasks with filters ("Show pending tasks")
   - Complete tasks by name ("Mark groceries as done")
   - Update task titles ("Rename groceries to buy vegetables")
   - Delete tasks ("Remove task 2")
   - Context-aware conversations

5. **MCP Integration**
   - MCP server exposing task CRUD tools
   - OpenAI Agents SDK for tool orchestration
   - User-scoped tool execution

6. **Conversation History**
   - Persistent conversation storage
   - Message history retrieval
   - Conversation context continuity

### Phase IV: Kubernetes Deployment

7. **Containerization**
   - Production-ready multi-stage Dockerfiles
   - Optimized image sizes (< 200MB frontend, < 300MB backend)
   - Non-root user execution
   - Health checks for K8s probes

8. **Helm Chart**
   - Complete Helm chart for application deployment
   - Configurable values for dev/prod environments
   - Secret management via K8s secrets
   - Service definitions (NodePort/ClusterIP)

9. **Local Kubernetes**
   - Minikube single-node cluster
   - Docker Desktop driver integration
   - kubectl-ai for natural language operations
   - kagent for agentic K8s management

## Project Structure

```
todo_p1/
├── frontend/           # Next.js application
│   └── src/
│       ├── app/        # Pages and API routes
│       ├── components/ # React components (incl. Chat UI)
│       └── lib/        # Auth, API client
├── backend/            # FastAPI application
│   └── app/
│       ├── routers/    # API endpoints (tasks, chat)
│       ├── mcp/        # MCP server and tools
│       └── models/     # SQLModel models
├── specs/              # Specifications and documentation
│   ├── features/       # Feature specs (auth, tasks, chatbot)
│   ├── api/            # API documentation
│   ├── database/       # Database schemas
│   ├── mcp/            # MCP tool specifications
│   ├── infrastructure/ # K8s/Docker specs (Phase IV)
│   └── todo-app/       # Main feature spec
├── helm/               # Helm charts
│   └── todo-chatbot/   # Main application chart
├── history/            # Prompt history records
└── .spec-kit/          # SpecKit configuration
```

## Getting Started

See [README.md](../README.md) for setup instructions.

## Related Documents

- [Architecture](./architecture.md) - System architecture and design decisions
- [Feature Spec](./todo-app/spec.md) - Detailed feature specifications
- [Implementation Plan](./todo-app/plan.md) - Implementation approach
- [Tasks](./todo-app/tasks.md) - Development tasks

### Phase III Specs

- [Chatbot Feature](./features/chatbot.md) - Agent behavior and NL examples
- [Chat API](./api/chat-endpoint.md) - Chat endpoint specification
- [MCP Tools](./mcp/tools.md) - MCP tool definitions
- [Conversation Schema](./database/conversation-schema.md) - Database models

### Phase IV Specs

- [Docker Containerization](./infrastructure/docker.md) - Dockerfile patterns and Gordon AI
- [Helm Chart](./infrastructure/helm-chart.md) - K8s deployment chart
- [Deployment Guide](./infrastructure/deployment.md) - Minikube setup and AI ops
- [Implementation Tasks](./infrastructure/tasks.md) - Sequential task breakdown
- [Implementation Plan](./phase4-implementation-plan.md) - Full step-by-step plan
