# Phase IV: Kubernetes Deployment Spec

## Overview

Local Kubernetes deployment using Minikube with AI-assisted operations via kubectl-ai and kagent.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | Latest | Container runtime |
| Minikube | 1.32+ | Local K8s cluster |
| kubectl | 1.28+ | K8s CLI |
| Helm | 3.14+ | K8s package manager |
| kubectl-ai | Latest | AI-powered kubectl |
| kagent | Latest | K8s agentic AI (optional) |

## Installation Commands

### Minikube

```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (PowerShell)
winget install Kubernetes.minikube
```

### kubectl-ai (Google's Natural Language kubectl)

```bash
# Install via Krew (kubectl plugin manager)
kubectl krew install ai

# Or direct installation
# See: https://github.com/GoogleContainerTools/kubectl-ai
```

### kagent (Kubernetes-native Agentic AI)

```bash
# Install kagent CLI
# See: https://github.com/kagent-ai/kagent
pip install kagent
```

## Minikube Setup

### Start Cluster

```bash
# Start with Docker driver (recommended)
minikube start --driver=docker --memory=4096 --cpus=2

# Verify cluster
kubectl cluster-info
kubectl get nodes

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Configure Docker Environment

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Now docker commands use Minikube's Docker
docker images  # Shows Minikube's images
```

### Build Images in Minikube

```bash
# Ensure you're using Minikube's Docker
eval $(minikube docker-env)

# Build frontend
docker build -t todo-frontend:latest ./frontend

# Build backend
docker build -t todo-backend:latest ./backend

# Verify images
docker images | grep todo
```

## Deployment Workflow

### Step 1: Start Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=2
```

### Step 2: Build Images

```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

### Step 3: Create Namespace

```bash
kubectl create namespace todo-chatbot
kubectl config set-context --current --namespace=todo-chatbot
```

### Step 4: Deploy with Helm

```bash
# Set secrets as environment variables
export DATABASE_URL="postgresql://..."
export BETTER_AUTH_SECRET="your-secret"
export OPENAI_API_KEY="sk-..."

# Install chart
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -w

# Check services
kubectl get services

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Step 6: Access Application

```bash
# Option 1: Minikube service (opens browser)
minikube service frontend --namespace todo-chatbot

# Option 2: Minikube tunnel (for LoadBalancer services)
minikube tunnel

# Option 3: Port forward
kubectl port-forward svc/frontend 3000:3000
```

## AI-Assisted Operations

### kubectl-ai Examples

```bash
# Deploy the chart
kubectl ai "deploy the todo-chatbot helm chart to namespace todo-chatbot"

# Check pod status
kubectl ai "show me the status of all pods in todo-chatbot namespace"

# Expose frontend
kubectl ai "expose the frontend service on port 3000 with NodePort"

# Troubleshoot crashes
kubectl ai "why is the backend pod crashing?"

# Scale deployment
kubectl ai "scale the backend deployment to 3 replicas"

# View logs
kubectl ai "show me the last 50 lines of frontend pod logs"

# Check resource usage
kubectl ai "show resource usage for all pods"

# Describe failing pod
kubectl ai "describe the pod that is in CrashLoopBackOff"

# Get secrets
kubectl ai "list all secrets in todo-chatbot namespace"

# Update image
kubectl ai "update the frontend deployment to use image todo-frontend:v1.0.1"

# Rollback
kubectl ai "rollback the frontend deployment to the previous version"
```

### kagent Examples

```bash
# Cluster health analysis
kagent "analyze cluster health and resource utilization"

# Pod troubleshooting
kagent "investigate why the backend pod keeps restarting"

# Scaling recommendations
kagent "recommend scaling settings for the todo-chatbot application"

# Security audit
kagent "audit the security posture of the todo-chatbot deployment"

# Cost optimization
kagent "suggest resource optimizations to reduce costs"

# Log analysis
kagent "analyze logs from the last hour for errors"

# Performance tuning
kagent "identify performance bottlenecks in the application"
```

## Common Operations

### View Logs

```bash
# Frontend logs
kubectl logs -l app.kubernetes.io/name=frontend -f

# Backend logs
kubectl logs -l app.kubernetes.io/name=backend -f

# All pods
kubectl logs -l helm.sh/chart=todo-chatbot -f
```

### Exec into Pod

```bash
# Frontend
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/name=frontend -o jsonpath='{.items[0].metadata.name}') -- sh

# Backend
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}') -- sh
```

### Restart Deployment

```bash
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend
```

### Update Configuration

```bash
# Update single value
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --set frontend.replicaCount=3

# Update with new values file
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-dev.yaml
```

### Check Resource Usage

```bash
# Pod resources
kubectl top pods

# Node resources
kubectl top nodes
```

## Troubleshooting Guide

### Pod Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# With kubectl-ai
kubectl ai "why is pod frontend-xxx not starting?"
```

### Image Pull Errors

```bash
# Verify image exists in Minikube
eval $(minikube docker-env)
docker images | grep todo

# Check if imagePullPolicy is correct (IfNotPresent for local)
kubectl get deployment frontend -o yaml | grep imagePullPolicy
```

### Connection Refused

```bash
# Check service endpoints
kubectl get endpoints

# Verify backend is reachable from frontend
kubectl exec -it <frontend-pod> -- wget -qO- http://backend:8000/health

# Check DNS
kubectl exec -it <frontend-pod> -- nslookup backend
```

### Database Connection Issues

```bash
# Check secrets are mounted
kubectl exec -it <backend-pod> -- printenv | grep DATABASE

# Test connection from pod
kubectl exec -it <backend-pod> -- python -c "from app.database import engine; print('OK')"
```

### Health Check Failures

```bash
# Check probe configuration
kubectl get deployment backend -o yaml | grep -A 10 livenessProbe

# Test health endpoint manually
kubectl exec -it <backend-pod> -- curl localhost:8000/health
```

## Network Architecture

```
                             ┌─────────────────────────────────┐
                             │      External Access             │
                             │  http://192.168.49.2:30000      │
                             └───────────────┬─────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Minikube Cluster                                   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         todo-chatbot Namespace                         │ │
│  │                                                                        │ │
│  │  ┌────────────────────┐              ┌────────────────────┐           │ │
│  │  │  Frontend Service  │              │  Backend Service   │           │ │
│  │  │  NodePort: 30000   │              │  ClusterIP: 8000   │           │ │
│  │  └─────────┬──────────┘              └─────────┬──────────┘           │ │
│  │            │                                   │                       │ │
│  │            ▼                                   ▼                       │ │
│  │  ┌────────────────────┐              ┌────────────────────┐           │ │
│  │  │  Frontend Pod(s)   │─────────────▶│  Backend Pod(s)    │           │ │
│  │  │  - Next.js         │   HTTP       │  - FastAPI         │           │ │
│  │  │  - Port 3000       │  backend:8000│  - Port 8000       │           │ │
│  │  └────────────────────┘              └─────────┬──────────┘           │ │
│  │                                                │                       │ │
│  │  ┌────────────────────┐                        │                       │ │
│  │  │      Secrets       │◀───────────────────────┘                       │ │
│  │  │  - DATABASE_URL    │                                                │ │
│  │  │  - AUTH_SECRET     │                                                │ │
│  │  │  - OPENAI_API_KEY  │                                                │ │
│  │  └────────────────────┘                                                │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                             │
                                             ▼
                             ┌─────────────────────────────────┐
                             │     Neon PostgreSQL (Cloud)      │
                             │  ep-xxx.region.aws.neon.tech    │
                             └─────────────────────────────────┘
```

## Cleanup

```bash
# Uninstall helm release
helm uninstall todo-chatbot

# Delete namespace
kubectl delete namespace todo-chatbot

# Stop Minikube
minikube stop

# Delete Minikube cluster (full reset)
minikube delete
```

## Acceptance Criteria

1. `minikube start` creates a running cluster
2. Images build successfully in Minikube's Docker
3. `helm install` deploys all resources without errors
4. Both frontend and backend pods reach Ready state
5. Frontend accessible via `minikube service` or tunnel
6. Chat functionality works (task CRUD via AI)
7. kubectl-ai commands work for operations
8. Database connection to Neon is successful
9. All secrets properly injected and working

## README Updates Required

After successful deployment, update README.md with:

1. Kubernetes/Minikube setup section
2. Helm installation commands
3. kubectl-ai usage examples
4. Troubleshooting guide
5. Architecture diagram showing K8s deployment
6. Screenshots of running application in K8s
