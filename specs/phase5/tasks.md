# Phase V: Implementation Tasks

## Task Overview

### Part A: Advanced Features (Tasks 1-25)
### Part B: Local Deployment - Minikube (Tasks 26-35)
### Part C: Cloud Deployment (Tasks 36-50)

---

## Part A: Advanced Features

| # | Task | Priority | Dependencies | Status |
|---|------|----------|--------------|--------|
| 1 | Update database schema (migrations) | P0 | - | [ ] |
| 2 | Update Task SQLModel with new fields | P0 | 1 | [ ] |
| 3 | Create Tag model and TaskTag junction | P0 | 1 | [ ] |
| 4 | Create TaskEvent model (audit log) | P1 | 1 | [ ] |
| 5 | Update task schemas (Pydantic) | P0 | 2, 3 | [ ] |
| 6 | Update tasks router - CRUD with new fields | P0 | 5 | [ ] |
| 7 | Create tags router | P0 | 3, 5 | [ ] |
| 8 | Add search endpoint (full-text) | P1 | 6 | [ ] |
| 9 | Add filter parameters to list tasks | P0 | 6 | [ ] |
| 10 | Add sort parameters to list tasks | P0 | 6 | [ ] |
| 11 | Update MCP tools with new fields | P0 | 6 | [ ] |
| 12 | Create event publishing service | P0 | 4 | [ ] |
| 13 | Integrate events into MCP tools | P0 | 11, 12 | [ ] |
| 14 | Create recurrence calculation utility | P1 | - | [ ] |
| 15 | Create Notification Service skeleton | P1 | - | [ ] |
| 16 | Create Recurring Task Service skeleton | P1 | 14 | [ ] |
| 17 | Update frontend TaskForm component | P0 | 6 | [ ] |
| 18 | Add DatePicker component | P0 | - | [ ] |
| 19 | Add PrioritySelector component | P0 | - | [ ] |
| 20 | Add TagInput component | P0 | 7 | [ ] |
| 21 | Add RecurrenceSelector component | P1 | - | [ ] |
| 22 | Update TaskItem with new fields display | P0 | 17-21 | [ ] |
| 23 | Add SearchBar component | P1 | 8 | [ ] |
| 24 | Add FilterPanel component | P0 | 9 | [ ] |
| 25 | Add SortSelector component | P0 | 10 | [ ] |

---

## Part B: Local Deployment (Minikube)

| # | Task | Priority | Dependencies | Status |
|---|------|----------|--------------|--------|
| 26 | Create Dapr component YAMLs | P0 | - | [ ] |
| 27 | Create Kafka cluster YAML (Strimzi) | P0 | - | [ ] |
| 28 | Create Kafka topics YAML | P0 | 27 | [ ] |
| 29 | Update Helm chart with Dapr annotations | P0 | 26 | [ ] |
| 30 | Create Notification Service Dockerfile | P0 | 15 | [ ] |
| 31 | Create Recurring Task Service Dockerfile | P0 | 16 | [ ] |
| 32 | Create K8s manifests for new services | P0 | 30, 31 | [ ] |
| 33 | Test Dapr + Kafka locally | P0 | 26-32 | [ ] |
| 34 | Test event flow end-to-end | P0 | 33 | [ ] |
| 35 | Verify all features on Minikube | P0 | 34 | [ ] |

---

## Part C: Cloud Deployment

| # | Task | Priority | Dependencies | Status |
|---|------|----------|--------------|--------|
| 36 | Create cloud K8s cluster (OKE/AKS/GKE) | P0 | - | [ ] |
| 37 | Configure kubectl for cloud cluster | P0 | 36 | [ ] |
| 38 | Install Dapr on cloud cluster | P0 | 37 | [ ] |
| 39 | Setup Kafka (Redpanda Cloud or self-hosted) | P0 | 37 | [ ] |
| 40 | Create container registry secrets | P0 | 37 | [ ] |
| 41 | Push images to GHCR | P0 | - | [ ] |
| 42 | Create values-prod.yaml | P0 | - | [ ] |
| 43 | Deploy application to cloud | P0 | 38-42 | [ ] |
| 44 | Configure LoadBalancer/Ingress | P0 | 43 | [ ] |
| 45 | Setup SSL/TLS certificates | P1 | 44 | [ ] |
| 46 | Create GitHub Actions workflow | P0 | - | [ ] |
| 47 | Configure GitHub secrets | P0 | 46 | [ ] |
| 48 | Test CI/CD pipeline | P0 | 46, 47 | [ ] |
| 49 | Setup monitoring (Prometheus/Grafana) | P1 | 43 | [ ] |
| 50 | Update README with cloud deployment | P0 | 35, 43 | [ ] |

---

## Detailed Task Descriptions

### Task 1: Update Database Schema

**Description:** Run Alembic migrations for Phase V schema changes.

**Steps:**
1. Install Alembic: `pip install alembic`
2. Initialize: `alembic init alembic`
3. Create migration: `alembic revision --autogenerate -m "phase5_schema"`
4. Run migration: `alembic upgrade head`

**Files:**
- `backend/alembic/versions/xxx_phase5_schema.py`

**Acceptance Criteria:**
- [ ] All new columns added to tasks table
- [ ] Tags and task_tags tables created
- [ ] task_events table created
- [ ] Indexes created

---

### Task 2: Update Task SQLModel

**Description:** Add new fields to Task model.

**File:** `backend/app/models/task.py`

**Changes:**
```python
class Task(SQLModel, table=True):
    # Existing fields...

    # New Phase V fields
    due_date: Optional[datetime] = Field(default=None)
    remind_at: Optional[datetime] = Field(default=None)
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    recurrence_rule: Optional[str] = Field(default=None, max_length=255)
    recurrence_end_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")
```

**Acceptance Criteria:**
- [ ] All new fields added
- [ ] Type hints correct
- [ ] Field validations work

---

### Task 3: Create Tag Model

**Description:** Create Tag model and TaskTag junction table.

**File:** `backend/app/models/tag.py`

**Acceptance Criteria:**
- [ ] Tag model with id, name, color, user_id
- [ ] TaskTag junction model
- [ ] Relationships defined

---

### Task 11: Update MCP Tools

**Description:** Add new parameters to MCP tools for advanced features.

**File:** `backend/app/mcp/tools.py`

**Changes to add_task:**
```python
@mcp.tool()
def add_task(
    title: str,
    user_id: str,
    due_date: str | None = None,
    priority: int | None = None,
    tags: list[str] | None = None,
    recurrence: str | None = None,
    remind_before_minutes: int = 60
) -> dict:
    """Create a new task with optional due date, priority, tags, and recurrence."""
```

**Changes to list_tasks:**
```python
@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    priority: int | None = None,
    tag: str | None = None,
    search: str | None = None,
    overdue: bool = False,
    sort_by: str = "due_date",
    sort_order: str = "asc"
) -> dict:
    """List tasks with filters and sorting."""
```

**Acceptance Criteria:**
- [ ] All new parameters added
- [ ] Parameters passed to execute_tool
- [ ] Docstrings updated for AI

---

### Task 12: Create Event Publishing Service

**Description:** Create service for publishing events via Dapr.

**File:** `backend/app/services/events.py`

```python
import httpx
from datetime import datetime
from uuid import uuid4

DAPR_URL = "http://localhost:3500"
PUBSUB_NAME = "kafka-pubsub"

async def publish_task_event(event_type: str, task: dict, user_id: str):
    """Publish task event to Kafka via Dapr."""
    ...

async def publish_reminder_event(task_id: str, title: str, due_at: datetime, remind_at: datetime, user_id: str):
    """Publish reminder event."""
    ...
```

**Acceptance Criteria:**
- [ ] Events published via Dapr HTTP API
- [ ] Proper event schema
- [ ] Error handling

---

### Task 15: Create Notification Service

**Description:** Create microservice to consume reminder events.

**Directory:** `services/notification/`

**Files:**
- `main.py` - FastAPI app with Dapr subscription
- `requirements.txt`
- `Dockerfile`

**Acceptance Criteria:**
- [ ] Subscribes to `reminders` topic
- [ ] Handles reminder.due events
- [ ] Logs notifications (actual push integration optional)

---

### Task 16: Create Recurring Task Service

**Description:** Create microservice to handle recurring tasks.

**Directory:** `services/recurring-task/`

**Files:**
- `main.py` - FastAPI app with Dapr subscription
- `recurrence.py` - RRULE calculation
- `requirements.txt`
- `Dockerfile`

**Acceptance Criteria:**
- [ ] Subscribes to `task-events` topic
- [ ] Creates next occurrence on task.completed
- [ ] Uses python-dateutil for RRULE parsing

---

### Task 26: Create Dapr Component YAMLs

**Description:** Create Dapr component configurations.

**Directory:** `k8s/dapr-components/`

**Files:**
- `pubsub.yaml` - Kafka pub/sub
- `statestore.yaml` - PostgreSQL state
- `secretstore.yaml` - K8s secrets

**Acceptance Criteria:**
- [ ] All components configured
- [ ] Scopes defined
- [ ] Secrets referenced properly

---

### Task 27: Create Kafka Cluster YAML

**Description:** Strimzi Kafka cluster definition.

**File:** `k8s/kafka/kafka-cluster.yaml`

**Acceptance Criteria:**
- [ ] Kafka cluster CRD defined
- [ ] Single replica for dev
- [ ] Ephemeral storage (for Minikube)

---

### Task 29: Update Helm Chart with Dapr

**Description:** Add Dapr sidecar annotations to Helm templates.

**Changes:**
- Add `dapr.io/enabled: "true"` annotations
- Add `dapr.io/app-id` and `dapr.io/app-port`
- Update values.yaml with Dapr config

**Acceptance Criteria:**
- [ ] Backend deployment has Dapr annotations
- [ ] Frontend deployment has Dapr annotations
- [ ] Helm lint passes

---

### Task 46: Create GitHub Actions Workflow

**Description:** CI/CD pipeline for automated deployment.

**File:** `.github/workflows/ci-cd.yaml`

**Jobs:**
1. Lint & Type Check
2. Run Tests
3. Build & Push Images
4. Deploy to Kubernetes

**Acceptance Criteria:**
- [ ] Runs on push to main
- [ ] Builds all images
- [ ] Deploys via Helm
- [ ] Health check after deploy

---

### Task 50: Update README

**Description:** Document Phase V features and deployment.

**Sections to add:**
- Advanced Features (due dates, priorities, tags, recurring)
- Event-Driven Architecture
- Dapr Integration
- Cloud Deployment (OKE/AKS/GKE)
- CI/CD Pipeline
- Monitoring

**Acceptance Criteria:**
- [ ] All new features documented
- [ ] Cloud setup instructions
- [ ] Architecture diagrams updated

---

## Implementation Order

### Week 1: Advanced Features
1. Database schema + models (Tasks 1-4)
2. Backend APIs (Tasks 5-10)
3. MCP tool updates (Task 11)
4. Event service (Tasks 12-13)

### Week 2: Frontend + Microservices
5. Frontend components (Tasks 17-25)
6. Microservices (Tasks 14-16)
7. Local testing

### Week 3: Kubernetes + Cloud
8. Dapr + Kafka config (Tasks 26-28)
9. Helm updates (Task 29)
10. Service Dockerfiles (Tasks 30-32)
11. Local Minikube testing (Tasks 33-35)

### Week 4: Cloud + CI/CD
12. Cloud cluster setup (Tasks 36-40)
13. Cloud deployment (Tasks 41-45)
14. CI/CD pipeline (Tasks 46-48)
15. Monitoring + docs (Tasks 49-50)

---

## Success Criteria

### Part A: Advanced Features
- [ ] All 8 features working (due dates, priorities, tags, reminders, recurring, search, filter, sort)
- [ ] MCP tools accept new parameters
- [ ] Chat commands work for all features

### Part B: Local Deployment
- [ ] Dapr installed and healthy
- [ ] Kafka cluster running
- [ ] All services communicate via Dapr
- [ ] Events flow correctly

### Part C: Cloud Deployment
- [ ] App deployed to cloud K8s
- [ ] CI/CD deploys on push
- [ ] SSL/TLS working
- [ ] Monitoring accessible
