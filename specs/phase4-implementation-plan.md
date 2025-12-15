# Phase IV Implementation Plan: Local Kubernetes Deployment

## Executive Summary

Containerize and deploy the full Phase III Todo AI Chatbot (frontend + backend + Neon DB) on a local Minikube cluster using Helm charts, with AI-assisted operations via kubectl-ai and kagent.

**Goal:** A running, accessible chatbot app in Kubernetes locally - proving scalability foundations.

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend Dockerfile | Exists (dev-only) | Single-stage, dev server |
| Backend Dockerfile | Exists (dev-only) | Single-stage, --reload flag |
| docker-compose.yml | Exists | Works for local dev |
| Helm Chart | Not created | Required |
| Minikube Setup | Not configured | Required |

## Phase IV Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Developer Machine                                │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────────────────────┐ │
│  │  Docker Desktop │    │              Minikube Cluster                   │ │
│  │                 │    │  ┌─────────────────────────────────────────┐    │ │
│  │  ┌───────────┐  │    │  │          todo-chatbot namespace         │    │ │
│  │  │ Gordon AI │  │    │  │                                         │    │ │
│  │  │ (optional)│  │    │  │  ┌─────────────┐  ┌─────────────┐      │    │ │
│  │  └───────────┘  │    │  │  │  Frontend   │  │  Backend    │      │    │ │
│  │                 │    │  │  │  Pod(s)     │  │  Pod(s)     │      │    │ │
│  │  Images:        │    │  │  │             │  │             │      │    │ │
│  │  - frontend:v1  │───▶│  │  │  NodePort   │  │  ClusterIP  │      │    │ │
│  │  - backend:v1   │    │  │  │  :30000     │  │  :8000      │      │    │ │
│  │                 │    │  │  └──────┬──────┘  └──────┬──────┘      │    │ │
│  └─────────────────┘    │  │         │                │             │    │ │
│                         │  │         └────────────────┘             │    │ │
│  ┌─────────────────┐    │  │                  │                     │    │ │
│  │   kubectl-ai    │───▶│  │  ┌───────────────▼───────────────┐    │    │ │
│  │   kagent        │    │  │  │           Secrets              │    │    │ │
│  └─────────────────┘    │  │  │  DATABASE_URL, AUTH_SECRET    │    │    │ │
│                         │  │  │  OPENAI_API_KEY               │    │    │ │
│                         │  │  └───────────────────────────────┘    │    │ │
│                         │  └─────────────────────────────────────────┘    │ │
│                         └─────────────────────────────────────────────────┘ │
│                                             │                               │
└─────────────────────────────────────────────┼───────────────────────────────┘
                                              │ HTTPS
                                              ▼
                              ┌─────────────────────────────────┐
                              │     Neon PostgreSQL (Cloud)      │
                              │  ep-xxx.region.aws.neon.tech    │
                              └─────────────────────────────────┘
```

## Implementation Steps

### Step 1: Prerequisites Setup (Estimated: 15 min)

#### 1.1 Install/Verify Tools

```bash
# Check Docker Desktop
docker --version

# Install Minikube (if not present)
# Linux:
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify kubectl
kubectl version --client

# Install Helm (if not present)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install kubectl-ai (optional but recommended)
kubectl krew install ai
```

#### 1.2 Enable Gordon AI (Optional)

1. Open Docker Desktop
2. Go to Settings → Features in development
3. Enable "Docker AI" checkbox
4. Restart Docker Desktop

**Verification:**
```bash
docker ai "hello, are you available?"
```

---

### Step 2: Update Dockerfiles for Production (Estimated: 30 min)

#### 2.1 Update Next.js Configuration

**File:** `frontend/next.config.js`

Add standalone output mode:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // ... existing config
}

module.exports = nextConfig
```

#### 2.2 Create Frontend .dockerignore

**File:** `frontend/.dockerignore`

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

#### 2.3 Update Frontend Dockerfile

**File:** `frontend/Dockerfile`

Create multi-stage production build:
- Stage 1: Install dependencies
- Stage 2: Build Next.js
- Stage 3: Minimal runtime image

Key requirements:
- Use `node:20-alpine` base
- Non-root user (`nextjs`)
- HEALTHCHECK directive
- Build args for environment variables

#### 2.4 Create Backend .dockerignore

**File:** `backend/.dockerignore`

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

#### 2.5 Update Backend Dockerfile

**File:** `backend/Dockerfile`

Create multi-stage production build:
- Stage 1: Build with gcc, install deps in venv
- Stage 2: Minimal runtime with venv copy

Key requirements:
- Use `python:3.11-slim` base
- Non-root user (`appuser`)
- HEALTHCHECK directive
- Configurable WORKERS env var

**Gordon AI Commands (if available):**
```bash
docker ai "optimize frontend/Dockerfile for Next.js 14 production with standalone output"
docker ai "optimize backend/Dockerfile for FastAPI production with non-root user"
```

---

### Step 3: Create Helm Chart Structure (Estimated: 45 min)

#### 3.1 Initialize Chart

```bash
mkdir -p helm/todo-chatbot
```

#### 3.2 Create Chart Files

**Files to create:**

| File | Purpose |
|------|---------|
| `helm/todo-chatbot/Chart.yaml` | Chart metadata |
| `helm/todo-chatbot/values.yaml` | Default values |
| `helm/todo-chatbot/values-dev.yaml` | Minikube overrides |
| `helm/todo-chatbot/templates/_helpers.tpl` | Template helpers |
| `helm/todo-chatbot/templates/secrets.yaml` | K8s secrets |
| `helm/todo-chatbot/templates/frontend/deployment.yaml` | Frontend deployment |
| `helm/todo-chatbot/templates/frontend/service.yaml` | Frontend service |
| `helm/todo-chatbot/templates/backend/deployment.yaml` | Backend deployment |
| `helm/todo-chatbot/templates/backend/service.yaml` | Backend service |
| `helm/todo-chatbot/templates/NOTES.txt` | Post-install notes |
| `helm/todo-chatbot/.helmignore` | Ignore patterns |

#### 3.3 Configure Values

**values.yaml key sections:**
- `frontend.image`, `frontend.service`, `frontend.resources`
- `backend.image`, `backend.service`, `backend.resources`
- `secrets.databaseUrl`, `secrets.betterAuthSecret`, `secrets.openaiApiKey`

**values-dev.yaml:**
- Lower resource limits for Minikube
- NodePort service type
- Single replica

---

### Step 4: Minikube Cluster Setup (Estimated: 15 min)

#### 4.1 Start Minikube

```bash
# Start cluster with Docker driver
minikube start --driver=docker --memory=4096 --cpus=2

# Verify
kubectl cluster-info
kubectl get nodes
```

#### 4.2 Configure Docker Environment

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify
docker images | head
```

---

### Step 5: Build and Load Images (Estimated: 20 min)

#### 5.1 Build Images in Minikube Docker

```bash
# Ensure using Minikube's Docker
eval $(minikube docker-env)

# Build frontend
docker build -t todo-frontend:latest ./frontend

# Build backend
docker build -t todo-backend:latest ./backend

# Verify
docker images | grep todo
```

#### 5.2 Verify Image Sizes

Target sizes:
- Frontend: < 200MB
- Backend: < 300MB

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep todo
```

---

### Step 6: Deploy with Helm (Estimated: 20 min)

#### 6.1 Create Namespace

```bash
kubectl create namespace todo-chatbot
kubectl config set-context --current --namespace=todo-chatbot
```

#### 6.2 Set Environment Variables

```bash
export DATABASE_URL="postgresql://your-neon-connection-string"
export BETTER_AUTH_SECRET="your-shared-secret"
export OPENAI_API_KEY="sk-your-openai-key"
```

#### 6.3 Lint Chart

```bash
helm lint ./helm/todo-chatbot
```

#### 6.4 Dry Run

```bash
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --dry-run --debug
```

#### 6.5 Install

```bash
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

---

### Step 7: Verify Deployment (Estimated: 15 min)

#### 7.1 Check Pods

```bash
kubectl get pods -w
# Wait until all pods are Running and Ready
```

#### 7.2 Check Services

```bash
kubectl get services
```

#### 7.3 Check Logs

```bash
# Frontend
kubectl logs -l app.kubernetes.io/name=frontend -f

# Backend
kubectl logs -l app.kubernetes.io/name=backend -f
```

#### 7.4 kubectl-ai Verification (if installed)

```bash
kubectl ai "show me the status of all pods in todo-chatbot namespace"
kubectl ai "are there any errors in the backend logs?"
```

---

### Step 8: Access Application (Estimated: 10 min)

#### 8.1 Get Service URL

```bash
# Option 1: Minikube service (opens browser)
minikube service frontend --namespace todo-chatbot

# Option 2: Get URL
minikube service frontend --namespace todo-chatbot --url
```

#### 8.2 Test Application

1. Open the URL in browser
2. Register/login
3. Create a task manually
4. Use chat to add a task: "Add buy groceries"
5. Verify task appears in list

---

### Step 9: AI-Assisted Operations Demo (Estimated: 15 min)

#### 9.1 kubectl-ai Examples

```bash
# Scale backend
kubectl ai "scale the backend deployment to 2 replicas"

# Check resource usage
kubectl ai "show resource usage for all pods"

# Troubleshoot (if any issues)
kubectl ai "why is the backend pod not ready?"

# View events
kubectl ai "show recent events in the namespace"
```

#### 9.2 kagent Examples (if installed)

```bash
# Cluster analysis
kagent "analyze cluster health"

# Performance check
kagent "identify performance bottlenecks"
```

---

### Step 10: Update Documentation (Estimated: 20 min)

#### 10.1 Update README.md

Add sections:
- Kubernetes Deployment (Minikube)
- Prerequisites (tools list)
- Quick Start commands
- kubectl-ai usage examples
- Troubleshooting guide

#### 10.2 Add Architecture Diagram

Include K8s architecture diagram showing:
- Minikube cluster
- Namespace
- Pods and services
- Secrets
- External Neon connection

#### 10.3 Screenshots

Capture:
- Running pods in terminal
- Application UI in browser
- Chat functionality working

---

## Task Breakdown Summary

| # | Task | Files | Priority |
|---|------|-------|----------|
| 1 | Install/verify prerequisites | - | P0 |
| 2 | Update next.config.js for standalone | `frontend/next.config.js` | P0 |
| 3 | Create frontend .dockerignore | `frontend/.dockerignore` | P0 |
| 4 | Update frontend Dockerfile (multi-stage) | `frontend/Dockerfile` | P0 |
| 5 | Create backend .dockerignore | `backend/.dockerignore` | P0 |
| 6 | Update backend Dockerfile (multi-stage) | `backend/Dockerfile` | P0 |
| 7 | Create Helm chart structure | `helm/todo-chatbot/*` | P0 |
| 8 | Create Chart.yaml | `helm/todo-chatbot/Chart.yaml` | P0 |
| 9 | Create values.yaml | `helm/todo-chatbot/values.yaml` | P0 |
| 10 | Create values-dev.yaml | `helm/todo-chatbot/values-dev.yaml` | P1 |
| 11 | Create _helpers.tpl | `helm/todo-chatbot/templates/_helpers.tpl` | P0 |
| 12 | Create secrets.yaml template | `helm/todo-chatbot/templates/secrets.yaml` | P0 |
| 13 | Create frontend deployment | `helm/todo-chatbot/templates/frontend/deployment.yaml` | P0 |
| 14 | Create frontend service | `helm/todo-chatbot/templates/frontend/service.yaml` | P0 |
| 15 | Create backend deployment | `helm/todo-chatbot/templates/backend/deployment.yaml` | P0 |
| 16 | Create backend service | `helm/todo-chatbot/templates/backend/service.yaml` | P0 |
| 17 | Create NOTES.txt | `helm/todo-chatbot/templates/NOTES.txt` | P1 |
| 18 | Start Minikube cluster | - | P0 |
| 19 | Build images in Minikube | - | P0 |
| 20 | Deploy with Helm | - | P0 |
| 21 | Verify deployment | - | P0 |
| 22 | Test application | - | P0 |
| 23 | Demo kubectl-ai operations | - | P1 |
| 24 | Update README | `README.md` | P1 |
| 25 | Commit and push | - | P0 |

---

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Minikube running | `kubectl get nodes` shows Ready |
| Images built | `docker images | grep todo` shows both |
| Image sizes optimal | Frontend < 200MB, Backend < 300MB |
| Helm lint passes | `helm lint ./helm/todo-chatbot` |
| Pods running | All pods in Running/Ready state |
| Frontend accessible | Browser opens via `minikube service` |
| Auth works | Can register and login |
| Tasks work | Can create/list/complete tasks |
| Chat works | AI chatbot creates tasks |
| DB connected | Tasks persist across pod restarts |
| kubectl-ai works | Natural language commands execute |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Minikube resource constraints | Use values-dev.yaml with lower limits |
| Image build failures | Fall back to Claude-generated Dockerfiles |
| Neon connection issues | Test connection from pod with curl |
| Auth token issues (K8s URLs differ) | Configure NEXT_PUBLIC_AUTH_URL correctly |
| kubectl-ai not available | Provide manual kubectl equivalents |

---

## Rollback Plan

If deployment fails:
```bash
# Uninstall helm release
helm uninstall todo-chatbot --namespace todo-chatbot

# Delete namespace
kubectl delete namespace todo-chatbot

# Reset to docker-compose development
docker-compose up --build
```

---

## Next Steps After Phase IV

After successful Phase IV completion, potential Phase V enhancements:
- CI/CD pipeline with GitHub Actions
- Cloud deployment (GKE/EKS/AKS)
- Horizontal Pod Autoscaler
- Ingress with TLS
- Monitoring with Prometheus/Grafana
