# Phase V: Dapr Integration Specification

## Overview

Dapr (Distributed Application Runtime) provides portable, event-driven runtime for building microservices. It runs as a sidecar next to each service and abstracts infrastructure concerns.

## Why Dapr?

| Without Dapr | With Dapr |
|--------------|-----------|
| Import Kafka, Redis, Postgres libraries | Single HTTP API for all |
| Connection strings in code | Dapr components (YAML config) |
| Manual retry logic | Built-in retries, circuit breakers |
| Service URLs hardcoded | Automatic service discovery |
| Secrets in env vars | Secure secret store integration |
| Vendor lock-in | Swap Kafka for RabbitMQ with config change |

## Dapr Building Blocks Used

| Building Block | Use Case | Component Type |
|----------------|----------|----------------|
| **Pub/Sub** | Kafka abstraction | `pubsub.kafka` |
| **State Management** | Conversation state | `state.postgresql` |
| **Service Invocation** | Service-to-service calls | Built-in |
| **Jobs API** | Scheduled reminders | Built-in |
| **Secrets** | API keys, credentials | `secretstores.kubernetes` |

---

## Architecture with Dapr

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER                                       │
│                                                                                       │
│  ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐        │
│  │    Frontend Pod     │   │    Backend Pod      │   │  Notification Pod   │        │
│  │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │        │
│  │ │ Next  │ │ Dapr  │ │   │ │FastAPI│ │ Dapr  │ │   │ │Notif  │ │ Dapr  │ │        │
│  │ │  App  │◀┼▶Sidecar│ │   │ │+ MCP  │◀┼▶Sidecar│ │   │ │Service│◀┼▶Sidecar│ │        │
│  │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │        │
│  └──────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘        │
│             │                         │                         │                    │
│             └─────────────────────────┼─────────────────────────┘                    │
│                                       │                                              │
│                          ┌────────────▼────────────┐                                 │
│                          │    DAPR COMPONENTS      │                                 │
│                          │  ┌──────────────────┐   │                                 │
│                          │  │ pubsub.kafka     │───┼────▶ Kafka Cluster              │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ state.postgresql │───┼────▶ Neon DB                    │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ secretstores.k8s │   │  (API keys, credentials)        │
│                          │  └──────────────────┘   │                                 │
│                          └─────────────────────────┘                                 │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Dapr Installation

### Local (Minikube)

```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Verify installation
dapr --version

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr pods
kubectl get pods -n dapr-system
```

### Cloud (AKS/GKE/OKE)

```bash
# Same process - Dapr is cloud-agnostic
dapr init -k --runtime-version 1.14.0

# Enable high availability for production
dapr init -k --enable-ha=true
```

---

## Dapr Components

### 1. Pub/Sub Component (Kafka)

**File:** `dapr-components/pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-chatbot
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"  # Local Kafka
    # For Redpanda Cloud:
    # - name: brokers
    #   value: "YOUR-CLUSTER.cloud.redpanda.com:9092"
    # - name: authType
    #   value: "password"
    # - name: saslUsername
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: username
    # - name: saslPassword
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: password
    - name: consumerGroup
      value: "todo-service"
    - name: initialOffset
      value: "oldest"
scopes:
  - backend
  - notification-service
  - recurring-task-service
```

### 2. State Store Component (PostgreSQL)

**File:** `dapr-components/statestore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-chatbot
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: todo-chatbot-secrets
        key: DATABASE_URL
    - name: tableName
      value: "dapr_state"
scopes:
  - backend
```

### 3. Secrets Store Component (Kubernetes)

**File:** `dapr-components/secretstore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-chatbot
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

---

## Pub/Sub Usage

### Publishing Events (Backend)

**Without Dapr:**
```python
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers="kafka:9092", ...)
producer.send("task-events", value=json.dumps(event).encode())
```

**With Dapr:**
```python
import httpx

DAPR_URL = "http://localhost:3500"

async def publish_event(topic: str, event_type: str, data: dict):
    """Publish event via Dapr sidecar."""
    await httpx.post(
        f"{DAPR_URL}/v1.0/publish/kafka-pubsub/{topic}",
        json={
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Usage
await publish_event("task-events", "task.created", {
    "task_id": str(task.id),
    "title": task.title,
    "user_id": user_id
})
```

### Subscribing to Events (Notification Service)

**File:** `notification-service/subscriptions.py`

```python
from fastapi import FastAPI, Request

app = FastAPI()

# Dapr subscription configuration
@app.get("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which topics to subscribe to."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminder"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task"
        }
    ]

@app.post("/events/reminder")
async def handle_reminder(request: Request):
    """Handle reminder events from Kafka via Dapr."""
    event = await request.json()

    # Process reminder
    await send_notification(
        user_id=event["data"]["user_id"],
        title=f"Reminder: {event['data']['title']}",
        due_at=event["data"]["due_at"]
    )

    return {"status": "SUCCESS"}

@app.post("/events/task")
async def handle_task_event(request: Request):
    """Handle task events for audit logging."""
    event = await request.json()

    # Log to audit table
    await log_task_event(event)

    return {"status": "SUCCESS"}
```

---

## Service Invocation

### Frontend → Backend Calls

**Without Dapr:**
```typescript
// Must know exact backend URL
const response = await fetch("http://backend:8000/api/chat", {
  method: "POST",
  headers: { "Authorization": `Bearer ${token}` },
  body: JSON.stringify({ message })
});
```

**With Dapr:**
```typescript
// Call via Dapr sidecar - automatic discovery, retries, mTLS
const response = await fetch("http://localhost:3500/v1.0/invoke/backend/method/api/chat", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "dapr-app-id": "backend"
  },
  body: JSON.stringify({ message })
});
```

---

## Jobs API (Scheduled Reminders)

### Schedule a Reminder

```python
DAPR_URL = "http://localhost:3500"

async def schedule_reminder(task_id: str, remind_at: datetime, user_id: str):
    """Schedule reminder using Dapr Jobs API."""
    job_name = f"reminder-{task_id}"

    await httpx.post(
        f"{DAPR_URL}/v1.0-alpha1/jobs/{job_name}",
        json={
            "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "type": "reminder"
            }
        }
    )

async def cancel_reminder(task_id: str):
    """Cancel scheduled reminder."""
    job_name = f"reminder-{task_id}"
    await httpx.delete(f"{DAPR_URL}/v1.0-alpha1/jobs/{job_name}")
```

### Handle Job Trigger

```python
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr calls this endpoint when job fires."""
    job_data = await request.json()

    if job_data["data"]["type"] == "reminder":
        # Publish to notification service
        await publish_event("reminders", "reminder.due", {
            "task_id": job_data["data"]["task_id"],
            "user_id": job_data["data"]["user_id"]
        })

    return {"status": "SUCCESS"}
```

---

## Secrets Management

### Access Secrets via Dapr

```python
async def get_secret(secret_name: str, key: str) -> str:
    """Get secret via Dapr Secrets API."""
    response = await httpx.get(
        f"{DAPR_URL}/v1.0/secrets/kubernetes-secrets/{secret_name}"
    )
    return response.json()[key]

# Usage
openai_key = await get_secret("todo-chatbot-secrets", "OPENAI_API_KEY")
```

---

## State Management

### Store/Retrieve Conversation State

```python
async def save_state(key: str, value: dict):
    """Save state via Dapr State API."""
    await httpx.post(
        f"{DAPR_URL}/v1.0/state/statestore",
        json=[{"key": key, "value": value}]
    )

async def get_state(key: str) -> dict | None:
    """Get state via Dapr State API."""
    response = await httpx.get(f"{DAPR_URL}/v1.0/state/statestore/{key}")
    if response.status_code == 200:
        return response.json()
    return None

async def delete_state(key: str):
    """Delete state via Dapr State API."""
    await httpx.delete(f"{DAPR_URL}/v1.0/state/statestore/{key}")

# Usage
await save_state(f"conversation-{conv_id}", {"messages": messages})
state = await get_state(f"conversation-{conv_id}")
```

---

## Kubernetes Deployment with Dapr

### Backend Deployment with Dapr Sidecar

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-chatbot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        # Dapr sidecar injection
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
        - name: backend
          image: todo-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
```

### Notification Service Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: todo-chatbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
        - name: notification-service
          image: notification-service:latest
          ports:
            - containerPort: 8001
```

---

## Dapr Dashboard

```bash
# Access Dapr dashboard
dapr dashboard -k -n todo-chatbot

# Opens http://localhost:8080 with:
# - Component status
# - Application list
# - Configuration view
# - Logs viewer
```

---

## Testing Dapr Locally

### Run with Dapr CLI

```bash
# Run backend with Dapr sidecar
cd backend
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 -- uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run notification service
cd notification-service
dapr run --app-id notification-service --app-port 8001 --dapr-http-port 3501 -- uvicorn main:app --host 0.0.0.0 --port 8001
```

### Test Pub/Sub

```bash
# Publish test event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "task.created", "data": {"task_id": "123", "title": "Test"}}'

# Check notification service logs for received event
```

---

## Acceptance Criteria

- [ ] Dapr installed on Kubernetes (`dapr init -k`)
- [ ] Pub/Sub component configured for Kafka
- [ ] State store component configured for PostgreSQL
- [ ] Backend publishes events via Dapr
- [ ] Notification service subscribes via Dapr
- [ ] Jobs API schedules reminders correctly
- [ ] Secrets accessed via Dapr Secrets API
- [ ] Service invocation works with automatic retries
- [ ] Dapr dashboard accessible
