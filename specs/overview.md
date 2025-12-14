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

### Phase I & II: Foundation

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

### Phase III: AI Chatbot

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
│   └── todo-app/       # Main feature spec
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
