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

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List user's tasks |
| POST | /api/tasks | Create a task |
| PATCH | /api/tasks/{id} | Update a task |
| DELETE | /api/tasks/{id} | Delete a task |
| GET | /health | Health check |

All task endpoints require `Authorization: Bearer <token>` header.

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
│   │   ├── components/       # TaskForm, TaskList, TaskItem
│   │   ├── lib/              # auth.ts, api.ts
│   │   └── types/            # TypeScript definitions
│   ├── Dockerfile
│   └── package.json
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── models/           # SQLModel models (Task)
│   │   ├── routers/          # API endpoints (/api/tasks)
│   │   ├── dependencies/     # JWT auth verification
│   │   └── schemas/          # Pydantic DTOs
│   ├── tests/                # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── specs/                    # Specifications
│   ├── features/             # Feature specs (auth, task-crud)
│   ├── api/                  # REST endpoint documentation
│   ├── database/             # Schema documentation
│   └── todo-app/             # Main feature spec/plan/tasks
├── docker-compose.yml        # Dev environment orchestration
├── .env.example              # Environment template
└── CLAUDE.md                 # AI assistant guidelines
```

## Security

- All secrets loaded from environment variables
- JWT tokens verified with shared secret
- User ownership enforced on all task operations
- CORS configured for frontend origin only
