# Phase IV: Helm Chart Specification

## Overview

Helm chart for deploying the Todo AI Chatbot application to Kubernetes, managing frontend, backend, and all required configurations.

## Chart Structure

```
helm/todo-chatbot/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── values-dev.yaml         # Development overrides (Minikube)
├── values-prod.yaml        # Production overrides
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── NOTES.txt           # Post-install instructions
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── secrets.yaml        # Shared secrets
└── .helmignore
```

## Chart.yaml

```yaml
apiVersion: v2
name: todo-chatbot
description: Todo AI Chatbot - Full-stack task management with AI
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - ai
  - nextjs
  - fastapi
maintainers:
  - name: MZS CodeWorks
    email: maintainer@example.com
```

## values.yaml (Default Configuration)

```yaml
# Global settings
global:
  namespace: todo-chatbot
  imagePullPolicy: IfNotPresent

# Frontend configuration
frontend:
  name: frontend
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: NodePort
    port: 3000
    nodePort: 30000
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    NEXT_PUBLIC_API_URL: "http://backend:8000"
    NEXT_PUBLIC_AUTH_URL: "http://localhost:30000"
  healthCheck:
    path: /
    port: 3000
    initialDelaySeconds: 10
    periodSeconds: 10

# Backend configuration
backend:
  name: backend
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    WORKERS: "2"
    AUTH_URL: "http://frontend:3000"
  healthCheck:
    path: /health
    port: 8000
    initialDelaySeconds: 15
    periodSeconds: 10

# Secrets (override in values-dev.yaml or via --set)
secrets:
  # Base64 encoded values (use `echo -n 'value' | base64`)
  databaseUrl: ""           # DATABASE_URL
  betterAuthSecret: ""      # BETTER_AUTH_SECRET
  openaiApiKey: ""          # OPENAI_API_KEY

# Ingress (optional, for production)
ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: todo.local
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
```

## Template Files

### templates/_helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-chatbot.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels for frontend
*/}}
{{- define "todo-chatbot.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ .Values.frontend.name }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Selector labels for backend
*/}}
{{- define "todo-chatbot.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ .Values.backend.name }}
app.kubernetes.io/component: backend
{{- end }}
```

### templates/secrets.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-secrets
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | b64enc | quote }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | b64enc | quote }}
```

### templates/frontend/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.frontend.name }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 4 }}
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Values.frontend.name }}
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.frontend.service.port }}
              protocol: TCP
          env:
            - name: NEXT_PUBLIC_API_URL
              value: {{ .Values.frontend.env.NEXT_PUBLIC_API_URL | quote }}
            - name: NEXT_PUBLIC_AUTH_URL
              value: {{ .Values.frontend.env.NEXT_PUBLIC_AUTH_URL | quote }}
            - name: BETTER_AUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-chatbot.fullname" . }}-secrets
                  key: BETTER_AUTH_SECRET
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-chatbot.fullname" . }}-secrets
                  key: DATABASE_URL
          livenessProbe:
            httpGet:
              path: {{ .Values.frontend.healthCheck.path }}
              port: {{ .Values.frontend.healthCheck.port }}
            initialDelaySeconds: {{ .Values.frontend.healthCheck.initialDelaySeconds }}
            periodSeconds: {{ .Values.frontend.healthCheck.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.frontend.healthCheck.path }}
              port: {{ .Values.frontend.healthCheck.port }}
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
```

### templates/frontend/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.frontend.name }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: http
      protocol: TCP
      name: http
      {{- if eq .Values.frontend.service.type "NodePort" }}
      nodePort: {{ .Values.frontend.service.nodePort }}
      {{- end }}
  selector:
    {{- include "todo-chatbot.frontend.selectorLabels" . | nindent 4 }}
```

### templates/backend/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.backend.name }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    {{- include "todo-chatbot.backend.selectorLabels" . | nindent 4 }}
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-chatbot.backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.backend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Values.backend.name }}
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.backend.service.port }}
              protocol: TCP
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-chatbot.fullname" . }}-secrets
                  key: DATABASE_URL
            - name: BETTER_AUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-chatbot.fullname" . }}-secrets
                  key: BETTER_AUTH_SECRET
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-chatbot.fullname" . }}-secrets
                  key: OPENAI_API_KEY
            - name: AUTH_URL
              value: {{ .Values.backend.env.AUTH_URL | quote }}
            - name: WORKERS
              value: {{ .Values.backend.env.WORKERS | quote }}
          livenessProbe:
            httpGet:
              path: {{ .Values.backend.healthCheck.path }}
              port: {{ .Values.backend.healthCheck.port }}
            initialDelaySeconds: {{ .Values.backend.healthCheck.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.healthCheck.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.backend.healthCheck.path }}
              port: {{ .Values.backend.healthCheck.port }}
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
```

### templates/backend/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.backend.name }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "todo-chatbot.backend.selectorLabels" . | nindent 4 }}
```

### templates/NOTES.txt

```
Thank you for installing {{ .Chart.Name }}!

Your Todo AI Chatbot is being deployed.

1. Get the frontend URL:
{{- if eq .Values.frontend.service.type "NodePort" }}
   export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ .Values.frontend.name }})
   export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
   echo "Frontend: http://$NODE_IP:$NODE_PORT"

   Or use Minikube:
   minikube service {{ .Values.frontend.name }} --url
{{- end }}

2. Check pod status:
   kubectl get pods -l app.kubernetes.io/name={{ .Values.frontend.name }}
   kubectl get pods -l app.kubernetes.io/name={{ .Values.backend.name }}

3. View logs:
   kubectl logs -l app.kubernetes.io/name={{ .Values.frontend.name }} -f
   kubectl logs -l app.kubernetes.io/name={{ .Values.backend.name }} -f

4. Troubleshoot with kubectl-ai:
   kubectl ai "why is the backend pod not ready?"
```

## values-dev.yaml (Minikube Development)

```yaml
# Minikube-specific overrides
frontend:
  replicaCount: 1
  service:
    type: NodePort
    nodePort: 30000
  resources:
    requests:
      memory: "64Mi"
      cpu: "50m"
    limits:
      memory: "256Mi"
      cpu: "250m"

backend:
  replicaCount: 1
  resources:
    requests:
      memory: "64Mi"
      cpu: "50m"
    limits:
      memory: "256Mi"
      cpu: "250m"

# Secrets - set these via --set or environment
# helm install todo-chatbot ./helm/todo-chatbot -f values-dev.yaml \
#   --set secrets.databaseUrl="$DATABASE_URL" \
#   --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
#   --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

## Helm Commands

### Install

```bash
# Install with default values
helm install todo-chatbot ./helm/todo-chatbot

# Install with secrets
helm install todo-chatbot ./helm/todo-chatbot \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.betterAuthSecret="your-secret" \
  --set secrets.openaiApiKey="sk-..."

# Install with values file
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-dev.yaml
```

### Upgrade

```bash
helm upgrade todo-chatbot ./helm/todo-chatbot
```

### Uninstall

```bash
helm uninstall todo-chatbot
```

### Debug

```bash
# Render templates locally
helm template todo-chatbot ./helm/todo-chatbot

# Dry run
helm install todo-chatbot ./helm/todo-chatbot --dry-run --debug

# Lint
helm lint ./helm/todo-chatbot
```

## Service Communication in Kubernetes

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│  ┌──────────────────┐          ┌──────────────────┐            │
│  │   Frontend Pod   │          │   Backend Pod    │            │
│  │  (todo-frontend) │          │  (todo-backend)  │            │
│  └────────┬─────────┘          └────────┬─────────┘            │
│           │                             │                       │
│           ▼                             ▼                       │
│  ┌──────────────────┐          ┌──────────────────┐            │
│  │ Frontend Service │          │ Backend Service  │            │
│  │   NodePort:30000 │          │   ClusterIP:8000 │            │
│  └────────┬─────────┘          └──────────────────┘            │
│           │                             ▲                       │
│           │                             │                       │
│           │    Internal DNS:            │                       │
│           │    backend:8000 ────────────┘                       │
│           │                                                     │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
    External Access
    http://NODE_IP:30000
```

## Secret Management

### Option 1: Values file (development only)

```yaml
# values-secrets.yaml (DO NOT COMMIT)
secrets:
  databaseUrl: "postgresql://..."
  betterAuthSecret: "your-secret"
  openaiApiKey: "sk-..."
```

### Option 2: Environment variables (recommended)

```bash
export DATABASE_URL="postgresql://..."
export BETTER_AUTH_SECRET="your-secret"
export OPENAI_API_KEY="sk-..."

helm install todo-chatbot ./helm/todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

### Option 3: External secrets operator (production)

For production, use Kubernetes External Secrets Operator with AWS Secrets Manager, HashiCorp Vault, etc.

## Acceptance Criteria

1. `helm lint ./helm/todo-chatbot` passes
2. `helm template` renders valid YAML
3. All pods reach Ready state
4. Health checks pass for both services
5. Frontend can communicate with backend via internal DNS
6. Secrets are properly injected
7. NOTES.txt provides useful post-install instructions
