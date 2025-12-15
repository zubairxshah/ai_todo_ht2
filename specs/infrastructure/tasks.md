# Phase IV: Implementation Tasks

## Task Overview

| # | Task | Priority | Dependencies | Status |
|---|------|----------|--------------|--------|
| 1 | Verify prerequisites installed | P0 | - | [X] |
| 2 | Enable Gordon AI (optional) | P1 | 1 | [X] |
| 3 | Create frontend .dockerignore | P0 | - | [X] |
| 4 | Update next.config.js for standalone | P0 | - | [X] |
| 5 | Create production frontend Dockerfile | P0 | 3, 4 | [X] |
| 6 | Create backend .dockerignore | P0 | - | [X] |
| 7 | Create production backend Dockerfile | P0 | 6 | [X] |
| 8 | Test Docker builds locally | P0 | 5, 7 | [ ] |
| 9 | Create Helm chart structure | P0 | - | [X] |
| 10 | Create Chart.yaml | P0 | 9 | [X] |
| 11 | Create values.yaml | P0 | 9 | [X] |
| 12 | Create _helpers.tpl | P0 | 9 | [X] |
| 13 | Create secrets.yaml template | P0 | 12 | [X] |
| 14 | Create frontend deployment.yaml | P0 | 12 | [X] |
| 15 | Create frontend service.yaml | P0 | 12 | [X] |
| 16 | Create backend deployment.yaml | P0 | 12 | [X] |
| 17 | Create backend service.yaml | P0 | 12 | [X] |
| 18 | Create NOTES.txt | P1 | 12 | [X] |
| 19 | Create values-dev.yaml | P1 | 11 | [X] |
| 20 | Lint Helm chart | P0 | 10-17 | [ ] |
| 21 | Start Minikube cluster | P0 | 1 | [ ] |
| 22 | Build images in Minikube | P0 | 5, 7, 21 | [ ] |
| 23 | Deploy with Helm | P0 | 20, 22 | [ ] |
| 24 | Verify pods running | P0 | 23 | [ ] |
| 25 | Test application access | P0 | 24 | [ ] |
| 26 | Test chat functionality | P0 | 25 | [ ] |
| 27 | Demo kubectl-ai operations | P1 | 24 | [ ] |
| 28 | Update README.md | P0 | 26 | [X] |
| 29 | Commit and push | P0 | 28 | [ ] |

---

## Task Details

### Task 1: Verify Prerequisites Installed

**Description**: Ensure all required tools are installed and accessible.

**Commands**:
```bash
# Check Docker
docker --version
# Expected: Docker version 24.x or higher

# Check Minikube
minikube version
# Expected: minikube version: v1.32.x or higher

# Check kubectl
kubectl version --client
# Expected: Client Version: v1.28.x or higher

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.14.x"...}
```

**Installation (if missing)**:
```bash
# Minikube (Linux)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl-ai (optional, via Krew)
kubectl krew install ai
```

**Acceptance Criteria**:
- [ ] `docker --version` returns 24.x+
- [ ] `minikube version` returns 1.32.x+
- [ ] `kubectl version --client` returns 1.28.x+
- [ ] `helm version` returns 3.14.x+

---

### Task 2: Enable Gordon AI (Optional)

**Description**: Enable Docker's AI assistant for intelligent Docker operations.

**Steps**:
1. Open Docker Desktop
2. Click gear icon (Settings)
3. Navigate to "Features in development"
4. Check "Enable Docker AI"
5. Click "Apply & Restart"

**Verification**:
```bash
docker ai "hello, are you available?"
```

**Acceptance Criteria**:
- [ ] Gordon responds to test query OR
- [ ] Document that Gordon is unavailable (proceed with Claude fallback)

---

### Task 3: Create Frontend .dockerignore

**File**: `frontend/.dockerignore`

**Content**:
```
# Dependencies
node_modules
.pnpm-store

# Build outputs
.next
out
build

# Development
.env*
.env.local
.env.development
.env.test

# IDE
.vscode
.idea
*.swp
*.swo

# Git
.git
.gitignore

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Tests
tests
__tests__
*.test.ts
*.test.tsx
*.spec.ts
*.spec.tsx
coverage
.nyc_output

# Documentation
*.md
docs

# Misc
.DS_Store
*.log
npm-debug.log*
```

**Acceptance Criteria**:
- [ ] File created at `frontend/.dockerignore`
- [ ] Excludes node_modules, .next, .env*, tests

---

### Task 4: Update next.config.js for Standalone

**File**: `frontend/next.config.js` (or `next.config.mjs`)

**Change**: Add `output: 'standalone'` to enable optimized production builds.

**Before**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {}

module.exports = nextConfig
```

**After**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}

module.exports = nextConfig
```

**Acceptance Criteria**:
- [ ] `output: 'standalone'` added to next.config.js
- [ ] `npm run build` succeeds and creates `.next/standalone` directory

---

### Task 5: Create Production Frontend Dockerfile

**File**: `frontend/Dockerfile`

**Gordon AI Command** (if available):
```bash
docker ai "create multi-stage Dockerfile for Next.js 14 with standalone output, non-root user, and healthcheck"
```

**Requirements**:
- 3-stage build: deps → builder → runner
- Base: `node:20-alpine`
- Non-root user: `nextjs:nodejs`
- HEALTHCHECK using wget
- Build args for NEXT_PUBLIC_* env vars
- Final image < 200MB

**Acceptance Criteria**:
- [ ] Multi-stage Dockerfile created
- [ ] Builds without errors
- [ ] Image size < 200MB
- [ ] Runs as non-root user
- [ ] HEALTHCHECK defined

---

### Task 6: Create Backend .dockerignore

**File**: `backend/.dockerignore`

**Content**:
```
# Python cache
__pycache__
*.py[cod]
*$py.class
*.so

# Virtual environments
venv
.venv
env
.env

# Environment files
.env*
*.env

# IDE
.vscode
.idea
*.swp
*.swo

# Git
.git
.gitignore

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Tests
tests
test_*.py
*_test.py
conftest.py
.pytest_cache
.coverage
htmlcov
coverage.xml

# Documentation
*.md
docs

# Build artifacts
*.egg-info
dist
build

# Misc
.DS_Store
*.log
```

**Acceptance Criteria**:
- [ ] File created at `backend/.dockerignore`
- [ ] Excludes __pycache__, venv, .env*, tests

---

### Task 7: Create Production Backend Dockerfile

**File**: `backend/Dockerfile`

**Gordon AI Command** (if available):
```bash
docker ai "create production FastAPI Dockerfile with multi-stage build, non-root user, healthcheck, and configurable workers"
```

**Requirements**:
- 2-stage build: builder → runner
- Base: `python:3.11-slim`
- Non-root user: `appuser`
- HEALTHCHECK using curl
- Configurable WORKERS env var
- Virtual environment for deps
- Final image < 300MB

**Acceptance Criteria**:
- [ ] Multi-stage Dockerfile created
- [ ] Builds without errors
- [ ] Image size < 300MB
- [ ] Runs as non-root user
- [ ] HEALTHCHECK defined

---

### Task 8: Test Docker Builds Locally

**Commands**:
```bash
# Build frontend
cd frontend
docker build -t todo-frontend:test .
docker images todo-frontend:test --format "{{.Size}}"

# Build backend
cd ../backend
docker build -t todo-backend:test .
docker images todo-backend:test --format "{{.Size}}"

# Test frontend runs
docker run --rm -p 3000:3000 todo-frontend:test &
curl -s http://localhost:3000 | head -5
docker stop $(docker ps -q --filter ancestor=todo-frontend:test)

# Test backend runs
docker run --rm -p 8000:8000 -e DATABASE_URL="postgresql://test" todo-backend:test &
sleep 3
curl -s http://localhost:8000/health
docker stop $(docker ps -q --filter ancestor=todo-backend:test)
```

**Acceptance Criteria**:
- [ ] Frontend builds successfully
- [ ] Backend builds successfully
- [ ] Frontend image < 200MB
- [ ] Backend image < 300MB
- [ ] Both containers start without errors

---

### Task 9: Create Helm Chart Structure

**Commands**:
```bash
mkdir -p helm/todo-chatbot/templates/frontend
mkdir -p helm/todo-chatbot/templates/backend
touch helm/todo-chatbot/.helmignore
```

**Structure**:
```
helm/todo-chatbot/
├── .helmignore
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
└── templates/
    ├── _helpers.tpl
    ├── NOTES.txt
    ├── secrets.yaml
    ├── frontend/
    │   ├── deployment.yaml
    │   └── service.yaml
    └── backend/
        ├── deployment.yaml
        └── service.yaml
```

**Acceptance Criteria**:
- [ ] Directory structure created
- [ ] .helmignore file created

---

### Task 10: Create Chart.yaml

**File**: `helm/todo-chatbot/Chart.yaml`

**Content**:
```yaml
apiVersion: v2
name: todo-chatbot
description: Todo AI Chatbot - Full-stack task management with AI assistant
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - ai
  - nextjs
  - fastapi
  - kubernetes
maintainers:
  - name: MZS CodeWorks
home: https://github.com/zubairxshah/ai_todo_ht2
```

**Acceptance Criteria**:
- [ ] Chart.yaml created with valid YAML
- [ ] Version set to 1.0.0

---

### Task 11: Create values.yaml

**File**: `helm/todo-chatbot/values.yaml`

See `@specs/infrastructure/helm-chart.md` for full content.

**Key Sections**:
- `frontend.*` - image, service, resources, env, healthCheck
- `backend.*` - image, service, resources, env, healthCheck
- `secrets.*` - databaseUrl, betterAuthSecret, openaiApiKey

**Acceptance Criteria**:
- [ ] values.yaml created with all sections
- [ ] Frontend uses NodePort:30000
- [ ] Backend uses ClusterIP:8000
- [ ] Resource limits defined

---

### Task 12: Create _helpers.tpl

**File**: `helm/todo-chatbot/templates/_helpers.tpl`

**Required Helpers**:
- `todo-chatbot.name`
- `todo-chatbot.fullname`
- `todo-chatbot.labels`
- `todo-chatbot.frontend.selectorLabels`
- `todo-chatbot.backend.selectorLabels`

**Acceptance Criteria**:
- [ ] All helper templates defined
- [ ] Labels include standard K8s metadata

---

### Task 13: Create secrets.yaml Template

**File**: `helm/todo-chatbot/templates/secrets.yaml`

**Content**: K8s Secret with DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY

**Acceptance Criteria**:
- [ ] Secret template created
- [ ] Values properly templated from .Values.secrets
- [ ] Type: Opaque

---

### Task 14: Create Frontend Deployment

**File**: `helm/todo-chatbot/templates/frontend/deployment.yaml`

**Requirements**:
- Deployment with configurable replicas
- Container with env vars from ConfigMap and Secrets
- Liveness and readiness probes
- Resource requests/limits

**Acceptance Criteria**:
- [ ] Deployment template created
- [ ] Environment variables injected
- [ ] Health probes configured
- [ ] Resources defined

---

### Task 15: Create Frontend Service

**File**: `helm/todo-chatbot/templates/frontend/service.yaml`

**Requirements**:
- NodePort service type (for Minikube access)
- Port 3000, NodePort 30000

**Acceptance Criteria**:
- [ ] Service template created
- [ ] NodePort configured

---

### Task 16: Create Backend Deployment

**File**: `helm/todo-chatbot/templates/backend/deployment.yaml`

**Requirements**:
- Similar to frontend deployment
- Additional OPENAI_API_KEY secret
- WORKERS env var

**Acceptance Criteria**:
- [ ] Deployment template created
- [ ] All secrets injected
- [ ] Health probes configured

---

### Task 17: Create Backend Service

**File**: `helm/todo-chatbot/templates/backend/service.yaml`

**Requirements**:
- ClusterIP service type (internal only)
- Port 8000

**Acceptance Criteria**:
- [ ] Service template created
- [ ] ClusterIP type

---

### Task 18: Create NOTES.txt

**File**: `helm/todo-chatbot/templates/NOTES.txt`

**Content**: Post-install instructions showing:
- How to get frontend URL
- How to check pod status
- How to view logs
- kubectl-ai troubleshooting examples

**Acceptance Criteria**:
- [ ] NOTES.txt created
- [ ] Instructions for Minikube access included

---

### Task 19: Create values-dev.yaml

**File**: `helm/todo-chatbot/values-dev.yaml`

**Content**: Minikube-specific overrides with lower resources

**Acceptance Criteria**:
- [ ] Dev values file created
- [ ] Lower resource limits for Minikube

---

### Task 20: Lint Helm Chart

**Commands**:
```bash
helm lint ./helm/todo-chatbot
helm template todo-chatbot ./helm/todo-chatbot --debug
```

**Acceptance Criteria**:
- [ ] `helm lint` passes with no errors
- [ ] `helm template` renders valid YAML

---

### Task 21: Start Minikube Cluster

**Commands**:
```bash
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Verify
kubectl cluster-info
kubectl get nodes

# Enable addons (optional)
minikube addons enable metrics-server
```

**kubectl-ai Alternative**:
```bash
kubectl ai "start a minikube cluster with 4GB memory"
```

**Acceptance Criteria**:
- [ ] Minikube running
- [ ] Node in Ready state

---

### Task 22: Build Images in Minikube

**Commands**:
```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Verify
docker images | grep todo
```

**Acceptance Criteria**:
- [ ] Both images built in Minikube
- [ ] Images visible via `docker images`

---

### Task 23: Deploy with Helm

**Commands**:
```bash
# Create namespace
kubectl create namespace todo-chatbot

# Set secrets
export DATABASE_URL="your-neon-connection-string"
export BETTER_AUTH_SECRET="your-shared-secret"
export OPENAI_API_KEY="sk-your-key"

# Install
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

**kubectl-ai Alternative**:
```bash
kubectl ai "deploy the todo-chatbot helm chart to namespace todo-chatbot"
```

**Acceptance Criteria**:
- [ ] Helm install succeeds
- [ ] Resources created in namespace

---

### Task 24: Verify Pods Running

**Commands**:
```bash
# Watch pods
kubectl get pods -n todo-chatbot -w

# Check events
kubectl get events -n todo-chatbot --sort-by='.lastTimestamp'

# Describe pods (if issues)
kubectl describe pods -n todo-chatbot
```

**kubectl-ai Commands**:
```bash
kubectl ai "show me the status of all pods in todo-chatbot namespace"
kubectl ai "why is the backend pod not ready?"
```

**Acceptance Criteria**:
- [ ] Frontend pod Running/Ready
- [ ] Backend pod Running/Ready
- [ ] No CrashLoopBackOff errors

---

### Task 25: Test Application Access

**Commands**:
```bash
# Get URL
minikube service frontend -n todo-chatbot --url

# Or open in browser
minikube service frontend -n todo-chatbot
```

**kubectl-ai Commands**:
```bash
kubectl ai "expose the frontend service and give me the URL"
```

**Acceptance Criteria**:
- [ ] Frontend URL accessible
- [ ] Login page loads

---

### Task 26: Test Chat Functionality

**Steps**:
1. Register or login to app
2. Open chat widget
3. Send: "Add buy groceries"
4. Verify task appears in list
5. Send: "Show my tasks"
6. Verify response lists tasks
7. Send: "Mark groceries as done"
8. Verify task marked complete

**Acceptance Criteria**:
- [ ] Can login/register
- [ ] Chat responds
- [ ] Tasks created via chat
- [ ] Tasks listed correctly
- [ ] Tasks can be completed

---

### Task 27: Demo kubectl-ai Operations

**Commands**:
```bash
# Scale backend
kubectl ai "scale the backend deployment to 2 replicas"

# Check resources
kubectl ai "show resource usage for all pods in todo-chatbot"

# View logs
kubectl ai "show me the last 20 lines of backend logs"

# Troubleshoot (if needed)
kubectl ai "why is the backend pod restarting?"
```

**kagent Commands** (if installed):
```bash
kagent "analyze cluster health"
kagent "recommend scaling for todo-chatbot"
```

**Acceptance Criteria**:
- [ ] kubectl-ai commands execute
- [ ] Scaling works
- [ ] Logs viewable

---

### Task 28: Update README.md

**Sections to Add**:
1. Kubernetes Deployment section
2. Prerequisites (Minikube, Helm, kubectl)
3. Quick start commands
4. kubectl-ai usage examples
5. Troubleshooting guide
6. Architecture diagram update

**Acceptance Criteria**:
- [ ] K8s section added to README
- [ ] Commands documented
- [ ] Prerequisites listed

---

### Task 29: Commit and Push

**Commands**:
```bash
git add .
git commit -m "Phase 4: Kubernetes deployment with Helm charts

- Production multi-stage Dockerfiles (frontend < 200MB, backend < 300MB)
- Helm chart with deployments, services, secrets
- Minikube local deployment verified
- kubectl-ai integration documented
- Updated README with K8s setup instructions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin main
```

**Acceptance Criteria**:
- [ ] All changes committed
- [ ] Pushed to GitHub
- [ ] CI passes (if configured)
