# Phase V: Cloud Deployment Specification

## Overview

Deploy the Todo AI Chatbot to production-grade Kubernetes on cloud providers (Azure AKS, Google GKE, or Oracle OKE).

## Cloud Provider Options

| Provider | Free Tier | Duration | Best For |
|----------|-----------|----------|----------|
| **Oracle OKE** | 4 OCPUs, 24GB RAM | **Always Free** | Learning, no time pressure |
| Azure AKS | $200 credits | 30 days | Azure ecosystem |
| Google GKE | $300 credits | 90 days | GCP ecosystem |

**Recommendation:** Oracle OKE for hackathon - no credit card charge after trial.

---

## Part B: Local Deployment (Minikube)

### Prerequisites

```bash
# Verify tools
minikube version   # 1.32.x+
kubectl version    # 1.28.x+
helm version       # 3.14.x+
dapr version       # 1.14.x+
```

### Start Minikube Cluster

```bash
# Start with adequate resources
minikube start --driver=docker --memory=6144 --cpus=4

# Verify
kubectl cluster-info
```

### Install Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr pods
kubectl get pods -n dapr-system
```

### Deploy Kafka (Strimzi)

```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka'

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# Wait for Kafka
kubectl wait kafka/todo-kafka --for=condition=Ready -n kafka --timeout=600s

# Create topics
kubectl apply -f k8s/kafka/kafka-topics.yaml
```

### Deploy Application

```bash
# Build images in Minikube
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
docker build -t notification-service:latest ./services/notification
docker build -t recurring-task-service:latest ./services/recurring-task

# Create namespace
kubectl create namespace todo-chatbot

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# Deploy microservices
kubectl apply -f k8s/services/
```

### Access Application

```bash
# Get frontend URL
minikube service frontend -n todo-chatbot

# Or use tunnel
minikube tunnel
```

---

## Part C: Cloud Deployment

### Option 1: Oracle OKE (Recommended)

#### Create OKE Cluster

1. **Sign up:** https://www.oracle.com/cloud/free/
2. **Create Compartment:**
   - Navigation → Identity → Compartments → Create
   - Name: `todo-chatbot`

3. **Create OKE Cluster:**
   - Navigation → Developer Services → Kubernetes Clusters (OKE)
   - Create Cluster → Quick Create
   - Name: `todo-chatbot-cluster`
   - Kubernetes Version: Latest
   - Node Shape: `VM.Standard.A1.Flex` (Always Free)
   - Number of nodes: 2
   - Node count per subnet: 1

4. **Configure kubectl:**
```bash
# Install OCI CLI
curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash

# Configure OCI CLI
oci setup config

# Get kubeconfig
oci ce cluster create-kubeconfig --cluster-id <cluster-ocid> --file ~/.kube/config

# Verify connection
kubectl get nodes
```

#### Deploy to OKE

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Install Dapr
dapr init -k

# Deploy Kafka (or use managed service)
kubectl apply -f k8s/kafka/

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Create secrets
kubectl create secret generic todo-chatbot-secrets \
  --namespace todo-chatbot \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY"

# Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  -f helm/todo-chatbot/values-prod.yaml
```

### Option 2: Azure AKS

#### Create AKS Cluster

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name todo-chatbot-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-chatbot-rg \
  --name todo-chatbot-aks \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-chatbot-rg --name todo-chatbot-aks

# Verify
kubectl get nodes
```

#### Deploy to AKS

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Install Dapr
dapr init -k

# Option A: Use Azure Event Hubs (Kafka-compatible)
# Create Event Hubs namespace in Azure Portal
# Update Dapr component with Event Hubs connection string

# Option B: Deploy Strimzi Kafka
kubectl apply -f k8s/kafka/

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  -f helm/todo-chatbot/values-prod.yaml
```

### Option 3: Google GKE

#### Create GKE Cluster

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Set project
gcloud config set project YOUR_PROJECT_ID

# Create cluster
gcloud container clusters create todo-chatbot-gke \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 4

# Get credentials
gcloud container clusters get-credentials todo-chatbot-gke --zone us-central1-a

# Verify
kubectl get nodes
```

#### Deploy to GKE

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Install Dapr
dapr init -k

# Deploy Kafka or use Cloud Pub/Sub with Dapr
kubectl apply -f k8s/kafka/

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  -f helm/todo-chatbot/values-prod.yaml
```

---

## Production Values File

**File:** `helm/todo-chatbot/values-prod.yaml`

```yaml
# Production configuration
global:
  environment: production

frontend:
  replicaCount: 2
  image:
    repository: YOUR_REGISTRY/todo-frontend
    tag: "1.0.0"
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  service:
    type: LoadBalancer  # Use LoadBalancer for cloud
    port: 3000

backend:
  replicaCount: 2
  image:
    repository: YOUR_REGISTRY/todo-backend
    tag: "1.0.0"
  env:
    WORKERS: "4"
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  service:
    type: ClusterIP
    port: 8000

# Enable autoscaling
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilization: 70

# Ingress for production
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: todo.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.yourdomain.com
```

---

## Container Registry Setup

### GitHub Container Registry (GHCR)

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push
docker build -t ghcr.io/USERNAME/todo-frontend:1.0.0 ./frontend
docker push ghcr.io/USERNAME/todo-frontend:1.0.0

docker build -t ghcr.io/USERNAME/todo-backend:1.0.0 ./backend
docker push ghcr.io/USERNAME/todo-backend:1.0.0
```

### Create Image Pull Secret

```bash
kubectl create secret docker-registry ghcr-secret \
  --namespace todo-chatbot \
  --docker-server=ghcr.io \
  --docker-username=USERNAME \
  --docker-password=$GITHUB_TOKEN
```

---

## Kafka on Cloud

### Option A: Redpanda Cloud (Recommended)

1. Sign up at https://redpanda.com/cloud
2. Create Serverless cluster
3. Create topics: `task-events`, `reminders`, `task-updates`
4. Update Dapr component with credentials

### Option B: Azure Event Hubs

```bash
# Create Event Hubs namespace
az eventhubs namespace create \
  --name todo-chatbot-eh \
  --resource-group todo-chatbot-rg \
  --location eastus \
  --sku Standard

# Create Event Hub (topic)
az eventhubs eventhub create \
  --name task-events \
  --namespace-name todo-chatbot-eh \
  --resource-group todo-chatbot-rg
```

Dapr component for Event Hubs:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.azure.eventhubs
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: eventhubs-secrets
        key: connectionString
    - name: consumerGroup
      value: "$Default"
```

### Option C: Google Cloud Pub/Sub

Dapr component for Pub/Sub:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.gcp.pubsub
  version: v1
  metadata:
    - name: projectId
      value: "YOUR_PROJECT_ID"
    - name: type
      value: "service_account"
    - name: privateKey
      secretKeyRef:
        name: gcp-secrets
        key: privateKey
    - name: clientEmail
      value: "service-account@project.iam.gserviceaccount.com"
```

---

## Monitoring Setup

### Prometheus + Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123
```

### Access Grafana

```bash
# Port forward
kubectl port-forward svc/prometheus-grafana 3001:80 -n monitoring

# Open http://localhost:3001
# Login: admin / admin123
```

### Dapr Dashboard

```bash
# Access Dapr dashboard
dapr dashboard -k -n todo-chatbot
```

---

## SSL/TLS Setup

### Install cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

---

## Health Checks & Readiness

### Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
```

### Readiness Probe
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

---

## Acceptance Criteria

### Local (Minikube)
- [ ] Minikube cluster running with 6GB RAM
- [ ] Dapr installed and healthy
- [ ] Kafka cluster running (Strimzi)
- [ ] All pods Running/Ready
- [ ] Application accessible via minikube tunnel

### Cloud (AKS/GKE/OKE)
- [ ] Cloud cluster created
- [ ] kubectl connected to cluster
- [ ] Images pushed to container registry
- [ ] Dapr installed on cloud cluster
- [ ] Kafka running (managed or self-hosted)
- [ ] Application deployed via Helm
- [ ] LoadBalancer/Ingress configured
- [ ] SSL/TLS certificates working
- [ ] Monitoring (Prometheus/Grafana) accessible
- [ ] All features functional
