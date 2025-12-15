# Phase IV: Docker Containerization Spec

## Overview

Production-ready containerization of the Todo AI Chatbot application using multi-stage Docker builds optimized for Kubernetes deployment.

**Constitution Compliance**: Section V (Containerization Best Practices)

## Current State

### Existing Dockerfiles (Development-Only)

| Service | Location | Issues |
|---------|----------|--------|
| Frontend | `frontend/Dockerfile` | Single-stage, dev server, no optimization |
| Backend | `backend/Dockerfile` | Single-stage, `--reload` flag, no optimization |

### Current Problems

1. **No multi-stage builds** - Large image sizes (~1GB+)
2. **Development commands** - `npm run dev`, `--reload` flags
3. **No layer caching optimization** - Slow rebuilds
4. **No security hardening** - Runs as root
5. **No health checks** - K8s can't probe readiness
6. **No .dockerignore** - Copies unnecessary files

## Requirements

### Frontend Dockerfile (Next.js)

| Requirement | Target |
|-------------|--------|
| Base image | `node:20-alpine` (matches local Node version) |
| Build type | Multi-stage (deps → build → runtime) |
| Final image size | < 200MB |
| User | Non-root (`nextjs:nodejs`) |
| Health check | `curl localhost:3000` or wget |
| Production command | `npm start` (not `npm run dev`) |

### Backend Dockerfile (FastAPI)

| Requirement | Target |
|-------------|--------|
| Base image | `python:3.11-slim` |
| Build type | Multi-stage (deps → runtime) |
| Final image size | < 300MB |
| User | Non-root (`appuser`) |
| Health check | `curl localhost:8000/health` |
| Production command | `uvicorn` without `--reload` |
| Workers | Configurable via `$WORKERS` env var |

## Gordon AI Integration

Gordon is Docker Desktop's AI agent for intelligent Docker operations.

**Constitution Compliance**: Section VI (AI-Assisted Operations)

### Enabling Gordon

1. Open Docker Desktop
2. Settings → Features in development → Enable Docker AI (checkbox)
3. Restart Docker Desktop
4. Use via CLI: `docker ai "<prompt>"`

### Gordon Commands - Analysis Phase

```bash
# Analyze existing Dockerfiles for issues
docker ai "analyze frontend/Dockerfile and list all production issues"
docker ai "analyze backend/Dockerfile for security vulnerabilities"
docker ai "what's wrong with this Dockerfile that runs as root?"

# Get optimization recommendations
docker ai "how can I reduce the size of my Node.js Docker image?"
docker ai "suggest layer caching improvements for Python dependencies"
```

### Gordon Commands - Generation Phase

```bash
# Generate optimized Dockerfiles
docker ai "create multi-stage Dockerfile for Next.js 14 with standalone output"
docker ai "create production FastAPI Dockerfile with non-root user and healthcheck"
docker ai "generate .dockerignore for a Next.js project"

# Optimize specific aspects
docker ai "optimize this Dockerfile for layer caching"
docker ai "add security hardening to this Dockerfile"
```

### Gordon Commands - Build & Debug Phase

```bash
# Build assistance
docker ai "why is my Next.js build failing with ENOENT error?"
docker ai "fix npm install failing in Docker multi-stage build"
docker ai "why is my Python dependencies stage so slow?"

# Security scanning
docker ai "scan todo-frontend:latest for vulnerabilities"
docker ai "check if my image has any CVEs"
```

### Gordon Commands - Optimization Phase

```bash
# Size optimization
docker ai "how can I make this 800MB image smaller?"
docker ai "compare alpine vs slim base images for my use case"

# Performance
docker ai "optimize Docker build time for CI/CD"
docker ai "set up BuildKit cache mounts for npm"
```

### Fallback (If Gordon Unavailable)

If Gordon is not available (Docker Desktop not installed or feature disabled):
1. Use Claude to generate Dockerfiles following the patterns below
2. Use `docker scan` for vulnerability scanning
3. Use `dive` tool for image layer analysis

## Production Dockerfile Patterns

### Frontend Multi-Stage Pattern

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Build-time env vars
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_AUTH_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_AUTH_URL=$NEXT_PUBLIC_AUTH_URL
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy only necessary files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

### Backend Multi-Stage Pattern

```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runner
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WORKERS=4

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $WORKERS"]
```

## Next.js Configuration for Standalone

To enable standalone output (required for optimized Docker builds), update `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // ... other config
}

module.exports = nextConfig
```

## Image Naming Convention

| Service | Image Name | Tag Pattern |
|---------|------------|-------------|
| Frontend | `todo-frontend` | `v1.0.0`, `latest`, `sha-abc1234` |
| Backend | `todo-backend` | `v1.0.0`, `latest`, `sha-abc1234` |

## Build Commands

### Local Development Build

```bash
# Build images
docker build -t todo-frontend:dev ./frontend
docker build -t todo-backend:dev ./backend

# Build with Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

### Production Build with Build Args

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://backend:8000 \
  --build-arg NEXT_PUBLIC_AUTH_URL=http://frontend:3000 \
  -t todo-frontend:v1.0.0 \
  ./frontend
```

## Security Checklist

- [ ] Non-root user in both images
- [ ] No secrets in image layers (use env vars at runtime)
- [ ] Minimal base images (alpine/slim)
- [ ] Health checks defined
- [ ] No development tools in production image
- [ ] .dockerignore files to exclude unnecessary files

## .dockerignore Files

### Frontend .dockerignore

```
node_modules
.next
.git
*.md
.env*
.dockerignore
Dockerfile
tests
coverage
.eslintcache
```

### Backend .dockerignore

```
__pycache__
*.pyc
.git
*.md
.env*
.dockerignore
Dockerfile
tests
.pytest_cache
.coverage
venv
.venv
```

## Acceptance Criteria

1. Frontend image builds successfully with `output: 'standalone'`
2. Backend image builds successfully with virtual environment
3. Both images run without errors
4. Health checks pass
5. Images are < 200MB (frontend) and < 300MB (backend)
6. Both run as non-root users
7. Gordon commands documented (or fallback to Claude-generated)
