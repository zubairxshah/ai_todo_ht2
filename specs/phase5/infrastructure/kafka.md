# Phase V: Kafka Event-Driven Architecture Specification

## Overview

Kafka transforms the Todo app from a simple CRUD application into an event-driven system where services communicate through events rather than direct API calls.

## Why Kafka?

| Without Kafka | With Kafka |
|---------------|------------|
| Reminder logic coupled with main app | Decoupled notification service |
| Recurring tasks processed synchronously | Async processing, no blocking |
| No activity history | Complete audit trail |
| Single client updates | Real-time multi-client sync |
| Tight coupling between services | Loose coupling, scalable |

---

## Event-Driven Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Todo Service   │────▶│  Kafka Topic    │────▶│  Notification   │────▶│  User Device    │
│  (Producer)     │     │  "reminders"    │     │  Service        │     │  (Push/Email)   │
│                 │     │                 │     │  (Consumer)     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `task-events` | Chat API (MCP Tools) | Recurring Task Service, Audit Service | All task CRUD operations |
| `reminders` | Chat API (due date set) | Notification Service | Scheduled reminder triggers |
| `task-updates` | Chat API | WebSocket Service | Real-time client sync |

---

## Event Schemas

### Task Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "task.created | task.updated | task.completed | task.deleted",
  "timestamp": "2025-12-15T10:30:00Z",
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries",
    "completed": false,
    "due_date": "2025-12-20T18:00:00Z",
    "priority": 1,
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
    "tags": ["shopping", "personal"],
    "user_id": "user-123"
  },
  "metadata": {
    "source": "chat-api",
    "correlation_id": "uuid"
  }
}
```

### Reminder Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "reminder.scheduled | reminder.due | reminder.cancelled",
  "timestamp": "2025-12-15T10:30:00Z",
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries",
    "due_at": "2025-12-20T18:00:00Z",
    "remind_at": "2025-12-20T17:00:00Z",
    "user_id": "user-123"
  }
}
```

### Task Update Event Schema (Real-time sync)

```json
{
  "event_id": "uuid",
  "event_type": "sync.task_changed",
  "timestamp": "2025-12-15T10:30:00Z",
  "data": {
    "task_id": "uuid",
    "change_type": "created | updated | deleted",
    "task": { /* full task object */ },
    "user_id": "user-123"
  }
}
```

---

## Kafka Provider Options

### Option 1: Redpanda Cloud (Recommended)

**Pros:**
- Free Serverless tier
- Kafka-compatible API
- No Zookeeper dependency
- Fast setup

**Setup:**
1. Sign up at https://redpanda.com/cloud
2. Create Serverless cluster
3. Create topics: `task-events`, `reminders`, `task-updates`
4. Copy bootstrap URL and credentials

**Dapr Component:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "YOUR-CLUSTER.cloud.redpanda.com:9092"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: consumerGroup
      value: "todo-service"
```

### Option 2: Self-Hosted (Strimzi on Kubernetes)

**Pros:**
- Free (just compute cost)
- Full control
- Good learning experience

**Setup:**
```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka'

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

**Kafka Cluster CRD:**
```yaml
# kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.7.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral  # Use persistent for production
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

**Create Topics:**
```yaml
# kafka-topics.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
```

**Dapr Component (Self-hosted):**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: initialOffset
      value: "oldest"
```

### Option 3: Redpanda on Kubernetes (Local)

**For Minikube development:**
```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install Redpanda
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --create-namespace \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi \
  --set storage.persistentVolume.size=10Gi
```

---

## Event Publishing (Backend)

### Via Dapr Pub/Sub

```python
# backend/app/services/events.py
import httpx
from datetime import datetime
from uuid import uuid4

DAPR_URL = "http://localhost:3500"
PUBSUB_NAME = "kafka-pubsub"

async def publish_task_event(
    event_type: str,
    task: dict,
    user_id: str
):
    """Publish task event to Kafka via Dapr."""
    event = {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            **task,
            "user_id": user_id
        },
        "metadata": {
            "source": "chat-api"
        }
    }

    await httpx.post(
        f"{DAPR_URL}/v1.0/publish/{PUBSUB_NAME}/task-events",
        json=event
    )

async def publish_reminder_event(
    task_id: str,
    title: str,
    due_at: datetime,
    remind_at: datetime,
    user_id: str
):
    """Publish reminder event."""
    event = {
        "event_id": str(uuid4()),
        "event_type": "reminder.scheduled",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "task_id": task_id,
            "title": title,
            "due_at": due_at.isoformat(),
            "remind_at": remind_at.isoformat(),
            "user_id": user_id
        }
    }

    await httpx.post(
        f"{DAPR_URL}/v1.0/publish/{PUBSUB_NAME}/reminders",
        json=event
    )
```

### Integration with MCP Tools

```python
# backend/app/mcp/tools.py
from app.services.events import publish_task_event, publish_reminder_event

async def execute_tool(tool_name: str, arguments: dict, user_id: str) -> dict:
    """Execute MCP tool and publish events."""

    if tool_name == "add_task":
        task = await create_task(...)

        # Publish event
        await publish_task_event("task.created", task.dict(), user_id)

        # Schedule reminder if due date set
        if task.due_date and task.remind_at:
            await publish_reminder_event(
                task_id=str(task.id),
                title=task.title,
                due_at=task.due_date,
                remind_at=task.remind_at,
                user_id=user_id
            )

        return {"success": True, "task": task.dict()}

    elif tool_name == "complete_task":
        task = await mark_task_complete(...)

        # Publish event (triggers recurring task service)
        await publish_task_event("task.completed", task.dict(), user_id)

        return {"success": True, "task": task.dict()}
```

---

## Event Consumption (Microservices)

### Notification Service

```python
# notification-service/main.py
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription configuration."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminder"
        }
    ]

@app.post("/events/reminder")
async def handle_reminder(request: Request):
    """Process reminder events."""
    event = await request.json()
    data = event.get("data", {})

    if event.get("event_type") == "reminder.due":
        # Send notification
        await send_push_notification(
            user_id=data["user_id"],
            title="Task Reminder",
            body=f"Don't forget: {data['title']}"
        )

    return {"status": "SUCCESS"}

async def send_push_notification(user_id: str, title: str, body: str):
    """Send push notification (implement with FCM, APNs, etc.)."""
    # TODO: Integrate with push notification service
    print(f"📱 Notification to {user_id}: {title} - {body}")
```

### Recurring Task Service

```python
# recurring-task-service/main.py
from fastapi import FastAPI, Request
from dateutil.rrule import rrulestr
from datetime import datetime
import httpx

app = FastAPI()
DAPR_URL = "http://localhost:3500"

@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task"
        }
    ]

@app.post("/events/task")
async def handle_task_event(request: Request):
    """Create next occurrence when recurring task completed."""
    event = await request.json()
    data = event.get("data", {})

    if event.get("event_type") == "task.completed":
        recurrence_rule = data.get("recurrence_rule")

        if recurrence_rule:
            # Calculate next occurrence
            next_due = calculate_next_occurrence(
                recurrence_rule,
                data.get("due_date")
            )

            if next_due:
                # Create next task via service invocation
                await httpx.post(
                    f"{DAPR_URL}/v1.0/invoke/backend/method/api/tasks",
                    json={
                        "title": data["title"],
                        "due_date": next_due.isoformat(),
                        "priority": data.get("priority"),
                        "recurrence_rule": recurrence_rule,
                        "parent_task_id": data["task_id"]
                    },
                    headers={"Authorization": f"Bearer {get_service_token()}"}
                )

    return {"status": "SUCCESS"}

def calculate_next_occurrence(rrule_str: str, last_due: str) -> datetime | None:
    """Calculate next occurrence based on RRULE."""
    try:
        rule = rrulestr(rrule_str, dtstart=datetime.fromisoformat(last_due))
        next_dates = list(rule[:2])  # Get next 2 occurrences
        if len(next_dates) > 1:
            return next_dates[1]
    except Exception:
        pass
    return None
```

---

## Testing Kafka Events

### Manual Testing with Dapr CLI

```bash
# Publish test event
dapr publish --publish-app-id backend --pubsub kafka-pubsub --topic task-events --data '{"event_type": "task.created", "data": {"task_id": "123", "title": "Test"}}'

# Check consumer logs
kubectl logs -l app=notification-service -f
```

### Using Kafka CLI (Redpanda)

```bash
# List topics
rpk topic list

# Produce message
rpk topic produce task-events

# Consume messages
rpk topic consume task-events --from-beginning
```

---

## Monitoring & Observability

### Kafka Metrics

```yaml
# For Strimzi - enable metrics
spec:
  kafka:
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: kafka-metrics-config.yml
```

### Dapr Metrics

```bash
# Dapr exposes Prometheus metrics on :9090
kubectl port-forward svc/dapr-sidecar 9090:9090
curl http://localhost:9090/metrics
```

---

## Acceptance Criteria

- [ ] Kafka cluster running (Strimzi or Redpanda)
- [ ] All topics created (`task-events`, `reminders`, `task-updates`)
- [ ] Dapr Pub/Sub component configured
- [ ] Backend publishes events on task operations
- [ ] Notification service receives reminder events
- [ ] Recurring task service creates next occurrences
- [ ] Events include all required fields
- [ ] Dead-letter handling for failed messages
