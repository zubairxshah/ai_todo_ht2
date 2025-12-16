# Phase V: CI/CD Pipeline Specification

## Overview

GitHub Actions workflow for automated testing, building, and deploying the Todo AI Chatbot to Kubernetes.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              GitHub Actions Pipeline                             │
│                                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐         │
│  │    Lint     │──▶│    Test     │──▶│    Build    │──▶│   Deploy    │         │
│  │  & Check    │   │   (pytest)  │   │  (Docker)   │   │   (Helm)    │         │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘         │
│                                                                                  │
│  Triggers: push to main, pull_request                                           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## GitHub Actions Workflow

**File:** `.github/workflows/ci-cd.yaml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  FRONTEND_IMAGE: ${{ github.repository }}/todo-frontend
  BACKEND_IMAGE: ${{ github.repository }}/todo-backend
  NOTIFICATION_IMAGE: ${{ github.repository }}/notification-service
  RECURRING_IMAGE: ${{ github.repository }}/recurring-task-service

jobs:
  # ==========================================================================
  # Job 1: Lint and Type Check
  # ==========================================================================
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt

      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci

      - name: Lint frontend
        working-directory: frontend
        run: npm run lint

      - name: Type check frontend
        working-directory: frontend
        run: npx tsc --noEmit

      - name: Install backend dependencies
        working-directory: backend
        run: |
          pip install -r requirements.txt
          pip install ruff mypy

      - name: Lint backend
        working-directory: backend
        run: ruff check app/

      - name: Type check backend
        working-directory: backend
        run: mypy app/ --ignore-missing-imports

  # ==========================================================================
  # Job 2: Test
  # ==========================================================================
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: todo_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt pytest pytest-asyncio pytest-cov

      - name: Run backend tests
        working-directory: backend
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/todo_test
          BETTER_AUTH_SECRET: test-secret-key-for-ci-testing-32ch
          AUTH_URL: http://localhost:3000
        run: pytest -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml
          flags: backend

  # ==========================================================================
  # Job 3: Build and Push Images
  # ==========================================================================
  build:
    name: Build & Push Images
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    permissions:
      contents: read
      packages: write

    outputs:
      frontend_tag: ${{ steps.meta-frontend.outputs.tags }}
      backend_tag: ${{ steps.meta-backend.outputs.tags }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (frontend)
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest

      - name: Extract metadata (backend)
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            NEXT_PUBLIC_API_URL=${{ secrets.NEXT_PUBLIC_API_URL }}
            NEXT_PUBLIC_AUTH_URL=${{ secrets.NEXT_PUBLIC_AUTH_URL }}

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push notification service
        uses: docker/build-push-action@v5
        with:
          context: ./services/notification
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.NOTIFICATION_IMAGE }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.NOTIFICATION_IMAGE }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push recurring task service
        uses: docker/build-push-action@v5
        with:
          context: ./services/recurring-task
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.RECURRING_IMAGE }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.RECURRING_IMAGE }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ==========================================================================
  # Job 4: Deploy to Kubernetes
  # ==========================================================================
  deploy:
    name: Deploy to Kubernetes
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    environment:
      name: production
      url: https://todo.yourdomain.com

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Install Helm
        uses: azure/setup-helm@v3
        with:
          version: 'v3.14.0'

      # For Oracle OKE
      - name: Configure OCI CLI
        if: ${{ vars.CLOUD_PROVIDER == 'oke' }}
        run: |
          mkdir -p ~/.oci
          echo "${{ secrets.OCI_CONFIG }}" > ~/.oci/config
          echo "${{ secrets.OCI_KEY }}" > ~/.oci/key.pem
          chmod 600 ~/.oci/key.pem

      - name: Get OKE kubeconfig
        if: ${{ vars.CLOUD_PROVIDER == 'oke' }}
        run: |
          oci ce cluster create-kubeconfig \
            --cluster-id ${{ secrets.OKE_CLUSTER_ID }} \
            --file ~/.kube/config \
            --region ${{ vars.OCI_REGION }}

      # For Azure AKS
      - name: Azure Login
        if: ${{ vars.CLOUD_PROVIDER == 'aks' }}
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get AKS kubeconfig
        if: ${{ vars.CLOUD_PROVIDER == 'aks' }}
        uses: azure/aks-set-context@v3
        with:
          resource-group: ${{ vars.AKS_RESOURCE_GROUP }}
          cluster-name: ${{ vars.AKS_CLUSTER_NAME }}

      # For Google GKE
      - name: Google Auth
        if: ${{ vars.CLOUD_PROVIDER == 'gke' }}
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}

      - name: Get GKE kubeconfig
        if: ${{ vars.CLOUD_PROVIDER == 'gke' }}
        uses: google-github-actions/get-gke-credentials@v2
        with:
          cluster_name: ${{ vars.GKE_CLUSTER_NAME }}
          location: ${{ vars.GKE_ZONE }}

      - name: Create/Update secrets
        run: |
          kubectl create namespace todo-chatbot --dry-run=client -o yaml | kubectl apply -f -

          kubectl create secret generic todo-chatbot-secrets \
            --namespace todo-chatbot \
            --from-literal=DATABASE_URL="${{ secrets.DATABASE_URL }}" \
            --from-literal=BETTER_AUTH_SECRET="${{ secrets.BETTER_AUTH_SECRET }}" \
            --from-literal=OPENAI_API_KEY="${{ secrets.OPENAI_API_KEY }}" \
            --dry-run=client -o yaml | kubectl apply -f -

          kubectl create secret docker-registry ghcr-secret \
            --namespace todo-chatbot \
            --docker-server=ghcr.io \
            --docker-username=${{ github.actor }} \
            --docker-password=${{ secrets.GITHUB_TOKEN }} \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy with Helm
        run: |
          helm upgrade --install todo-chatbot ./helm/todo-chatbot \
            --namespace todo-chatbot \
            --set frontend.image.repository=${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }} \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.repository=${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }} \
            --set backend.image.tag=${{ github.sha }} \
            --set global.imagePullSecrets[0]=ghcr-secret \
            -f helm/todo-chatbot/values-prod.yaml \
            --wait \
            --timeout 10m

      - name: Deploy microservices
        run: |
          kubectl apply -f k8s/services/ -n todo-chatbot

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/frontend -n todo-chatbot
          kubectl rollout status deployment/backend -n todo-chatbot
          kubectl get pods -n todo-chatbot

      - name: Run smoke tests
        run: |
          # Wait for pods to be ready
          kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend -n todo-chatbot --timeout=120s

          # Get backend pod
          BACKEND_POD=$(kubectl get pod -l app.kubernetes.io/name=backend -n todo-chatbot -o jsonpath='{.items[0].metadata.name}')

          # Health check
          kubectl exec $BACKEND_POD -n todo-chatbot -- curl -s http://localhost:8000/health

  # ==========================================================================
  # Job 5: Notify
  # ==========================================================================
  notify:
    name: Notify on Failure
    runs-on: ubuntu-latest
    needs: [lint, test, build, deploy]
    if: failure()

    steps:
      - name: Send failure notification
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload: |
            {
              "text": "❌ CI/CD Pipeline Failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*CI/CD Pipeline Failed*\n\nRepository: ${{ github.repository }}\nBranch: ${{ github.ref_name }}\nCommit: ${{ github.sha }}\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Shared auth secret |
| `OPENAI_API_KEY` | OpenAI API key |
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `NEXT_PUBLIC_AUTH_URL` | Auth URL |

### Cloud Provider Secrets

**Oracle OKE:**
| Secret | Description |
|--------|-------------|
| `OCI_CONFIG` | OCI CLI config file content |
| `OCI_KEY` | OCI API private key |
| `OKE_CLUSTER_ID` | OKE cluster OCID |

**Azure AKS:**
| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Azure service principal JSON |

**Google GKE:**
| Secret | Description |
|--------|-------------|
| `GCP_CREDENTIALS` | GCP service account JSON |

---

## GitHub Repository Variables

| Variable | Description |
|----------|-------------|
| `CLOUD_PROVIDER` | `oke`, `aks`, or `gke` |
| `OCI_REGION` | e.g., `us-ashburn-1` |
| `AKS_RESOURCE_GROUP` | Azure resource group |
| `AKS_CLUSTER_NAME` | AKS cluster name |
| `GKE_CLUSTER_NAME` | GKE cluster name |
| `GKE_ZONE` | e.g., `us-central1-a` |

---

## Pull Request Workflow

**File:** `.github/workflows/pr-check.yaml`

```yaml
name: PR Check

on:
  pull_request:
    branches: [main]

jobs:
  check:
    name: PR Validation
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd frontend && npm ci
          cd ../backend && pip install -r requirements.txt

      - name: Lint
        run: |
          cd frontend && npm run lint
          cd ../backend && pip install ruff && ruff check app/

      - name: Build frontend
        working-directory: frontend
        run: npm run build

      - name: Test backend
        working-directory: backend
        env:
          DATABASE_URL: sqlite:///./test.db
          BETTER_AUTH_SECRET: test-secret
          AUTH_URL: http://localhost:3000
        run: |
          pip install pytest
          pytest -v

      - name: Helm lint
        run: helm lint ./helm/todo-chatbot
```

---

## Branch Protection Rules

Configure in GitHub → Settings → Branches:

1. **Require pull request reviews**
   - Required approving reviews: 1
   - Dismiss stale pull request approvals

2. **Require status checks**
   - Require branches to be up to date
   - Status checks:
     - `PR Validation`
     - `Lint & Type Check`
     - `Run Tests`

3. **Require signed commits** (optional)

---

## Deployment Environments

### Setup in GitHub → Settings → Environments

**Production:**
- Required reviewers: 1
- Wait timer: 5 minutes
- Deployment branches: `main` only

---

## Rollback Strategy

```bash
# List Helm releases
helm history todo-chatbot -n todo-chatbot

# Rollback to previous version
helm rollback todo-chatbot 1 -n todo-chatbot

# Or rollback via kubectl
kubectl rollout undo deployment/backend -n todo-chatbot
kubectl rollout undo deployment/frontend -n todo-chatbot
```

---

## Acceptance Criteria

- [ ] Lint job passes for frontend and backend
- [ ] Tests run with PostgreSQL service container
- [ ] Images built and pushed to GHCR
- [ ] Helm deployment succeeds
- [ ] Health check passes after deployment
- [ ] Rollback procedure documented
- [ ] Branch protection rules configured
- [ ] Secrets properly configured
- [ ] Notifications on failure
