# Todo P1

A full-stack Todo application built with Next.js and FastAPI.

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Auth**: Better Auth client

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL
- **Auth**: JWT verification with shared secret

## Features

- User registration and authentication
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Inline task editing
- User ownership enforcement (users can only access their own tasks)
- **AI Chatbot** - Natural language task management via MCP tools
- **Real-time notifications** - Toast notifications for task updates
- **SSE Streaming** - Live chat responses with tool execution feedback

## AI Chatbot (Phase III)

The app includes an AI-powered chatbot that can manage your tasks through natural conversation.

### Chat Commands Examples

| You Say | AI Does |
|---------|---------|
| "Add buy groceries" | Creates a new task |
| "Show my tasks" | Lists all your tasks |
| "Show pending tasks" | Lists incomplete tasks |
| "Mark groceries as done" | Completes the matching task |
| "Delete the groceries task" | Removes the task |
| "Rename groceries to buy vegetables" | Updates task title |

### Demo

**Adding a task via chat:**
```
User: Add a task to call mom tomorrow
AI: Added task: 'call mom tomorrow'
    You now have 3 tasks (2 pending, 1 completed).
```

**Listing tasks:**
```
User: Show my pending tasks
AI: Your tasks:
    1. [ ] Call mom tomorrow
    2. [ ] Buy groceries
    2 pending tasks.
```

**Completing a task:**
```
User: Mark call mom as done
AI: Marked 'call mom tomorrow' as done!
    You now have 1 pending task.
```

## Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Neon PostgreSQL database

### Environment Variables

1. Copy the example files:

```bash
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

2. Fill in the values:

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-shared-secret
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

**Backend (.env)**:
```
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-shared-secret
OPENAI_API_KEY=sk-proj-xxx  # Required for AI chatbot
```

**Important**: `BETTER_AUTH_SECRET` must be the same in both frontend and backend.

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## API Endpoints

### Task Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List user's tasks |
| POST | /api/tasks | Create a task |
| PATCH | /api/tasks/{id} | Update a task |
| DELETE | /api/tasks/{id} | Delete a task |

### AI Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/chat | Send message to AI (JSON response) |
| POST | /api/chatkit | Send message to AI (SSE streaming) |
| GET | /api/chatkit/threads | List conversation threads |
| GET | /api/chatkit/threads/{id} | Get thread with messages |
| DELETE | /api/chatkit/threads/{id} | Delete a thread |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| * | /mcp | MCP Server (Streamable HTTP) |

All endpoints (except /health and /mcp) require `Authorization: Bearer <token>` header.

## Docker Development

### Quick Start with Docker

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your values:
#    - BETTER_AUTH_SECRET (generate with: openssl rand -base64 32)
#    - DATABASE_URL (your Neon connection string)

# 3. Start all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

### With Local PostgreSQL

```bash
# Start with local database (no Neon required)
docker-compose --profile local-db up --build

# Update .env to use local DB:
# DATABASE_URL=postgresql://postgres:postgres@db:5432/todo_p1
```

### Docker Commands

```bash
docker-compose up -d          # Start in background
docker-compose logs -f        # View logs
docker-compose down           # Stop all services
docker-compose down -v        # Stop and remove volumes
docker-compose build --no-cache  # Rebuild images
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

## Project Structure

```
todo_p1/
├── frontend/                 # Next.js 14 application
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── dashboard/    # Task management (protected)
│   │   │   ├── login/        # Login page
│   │   │   └── register/     # Registration page
│   │   ├── components/
│   │   │   ├── Chat/         # ChatWidget, ChatKitWidget
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   └── ToastNotification.tsx
│   │   ├── lib/
│   │   │   ├── auth.ts       # Better Auth client
│   │   │   ├── api.ts        # REST API client
│   │   │   ├── chat-api.ts   # Chat API client
│   │   │   └── task-events.ts # Real-time event emitter
│   │   └── types/            # TypeScript definitions
│   ├── Dockerfile
│   └── package.json
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── models/           # SQLModel models (Task, Message, Conversation)
│   │   ├── routers/
│   │   │   ├── tasks.py      # Task CRUD endpoints
│   │   │   ├── chat.py       # AI chat endpoint (JSON)
│   │   │   └── chatkit.py    # ChatKit SSE streaming
│   │   ├── agent/            # AI agent implementation
│   │   │   └── runner.py     # OpenAI function calling
│   │   ├── mcp/              # MCP tools & server
│   │   │   ├── tools.py      # Tool implementations
│   │   │   └── server.py     # FastMCP server
│   │   ├── dependencies/     # JWT auth verification
│   │   └── schemas/          # Pydantic DTOs
│   ├── tests/                # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── specs/                    # Specifications
│   ├── features/             # Feature specs (auth, task-crud, chatbot)
│   ├── api/                  # REST endpoint documentation
│   ├── database/             # Schema documentation
│   ├── infrastructure/       # K8s/Docker specs (Phase IV)
│   └── todo-app/             # Main feature spec/plan/tasks
├── helm/                     # Helm charts
│   └── todo-chatbot/         # Main application chart
│       ├── Chart.yaml        # Chart metadata
│       ├── values.yaml       # Default values
│       ├── values-dev.yaml   # Minikube overrides
│       └── templates/        # K8s manifests
├── docker-compose.yml        # Dev environment orchestration
├── .env.example              # Environment template
└── CLAUDE.md                 # AI assistant guidelines
```

## Kubernetes Deployment (Phase IV)

Deploy the Todo AI Chatbot to a local Kubernetes cluster using Minikube and Helm.

### Prerequisites

```bash
# Required tools
docker --version      # Docker 24.x+
minikube version      # Minikube 1.32.x+
kubectl version       # kubectl 1.28.x+
helm version          # Helm 3.14.x+

# Optional (AI-assisted ops)
kubectl krew install ai  # kubectl-ai for natural language K8s
```

### Quick Start with Minikube

```bash
# 1. Start Minikube cluster
minikube start --driver=docker --memory=4096 --cpus=2

# 2. Use Minikube's Docker daemon
eval $(minikube docker-env)

# 3. Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# 4. Create namespace and deploy
kubectl create namespace todo-chatbot

# 5. Set your secrets
export DATABASE_URL="postgresql://your-neon-connection-string"
export BETTER_AUTH_SECRET="your-shared-secret"
export OPENAI_API_KEY="sk-your-key"

# 6. Install with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# 7. Access the application
minikube service frontend -n todo-chatbot
```

### kubectl-ai Commands

If you have kubectl-ai installed, use natural language for K8s operations:

```bash
# Check status
kubectl ai "show me the status of all pods in todo-chatbot namespace"

# Scale
kubectl ai "scale the backend deployment to 2 replicas"

# Troubleshoot
kubectl ai "why is the backend pod not ready?"
kubectl ai "show the last 50 lines of frontend logs"

# Resources
kubectl ai "show resource usage for all pods in todo-chatbot"
```

### Helm Commands

```bash
# Upgrade deployment
helm upgrade todo-chatbot ./helm/todo-chatbot -n todo-chatbot

# View status
helm status todo-chatbot -n todo-chatbot

# Uninstall
helm uninstall todo-chatbot -n todo-chatbot

# Lint chart
helm lint ./helm/todo-chatbot
```

### Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  todo-chatbot namespace                    │  │
│  │                                                            │  │
│  │  ┌─────────────────┐        ┌─────────────────┐           │  │
│  │  │  Frontend Pod   │        │  Backend Pod    │           │  │
│  │  │  (Next.js)      │───────▶│  (FastAPI)      │           │  │
│  │  │  NodePort:30000 │        │  ClusterIP:8000 │           │  │
│  │  └─────────────────┘        └────────┬────────┘           │  │
│  │                                      │                     │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                    Secrets                           │  │  │
│  │  │  DATABASE_URL | BETTER_AUTH_SECRET | OPENAI_API_KEY │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   Neon PostgreSQL (Cloud)
```

## Security

- All secrets loaded from environment variables
- JWT tokens verified with shared secret
- User ownership enforced on all task operations
- CORS configured for frontend origin only
- **K8s secrets** for sensitive data in deployments
- **Non-root containers** for security hardening
