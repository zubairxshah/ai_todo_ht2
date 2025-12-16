# Phase V: Advanced Cloud Deployment - Overview

## Executive Summary

Phase V transforms the Todo AI Chatbot from a simple CRUD application into an enterprise-grade, event-driven microservices architecture deployed on production Kubernetes (AKS/GKE/OKE) with Dapr runtime and Kafka messaging.

## Objectives

1. **Advanced Features** - Recurring tasks, due dates, reminders, priorities, tags, search/filter
2. **Event-Driven Architecture** - Kafka for decoupled microservices communication
3. **Distributed Runtime** - Dapr for portable, cloud-native application patterns
4. **Production Deployment** - AKS/GKE/OKE with CI/CD, monitoring, and logging

## Phase V Components

### Part A: Advanced Features

| Feature | Category | Description |
|---------|----------|-------------|
| Recurring Tasks | Advanced | Auto-create next occurrence when completed |
| Due Dates | Advanced | Set task deadlines |
| Reminders | Advanced | Scheduled notifications before due date |
| Priorities | Intermediate | High/Medium/Low task priority |
| Tags | Intermediate | Categorize tasks with labels |
| Search | Intermediate | Full-text search across tasks |
| Filter | Intermediate | Filter by status, priority, tags, dates |
| Sort | Intermediate | Sort by date, priority, title |

### Part B: Local Deployment (Minikube)

| Component | Purpose |
|-----------|---------|
| Kafka (Strimzi/Redpanda) | Event streaming |
| Dapr | Distributed application runtime |
| Notification Service | Process reminder events |
| Recurring Task Service | Handle recurring task creation |

### Part C: Cloud Deployment

| Component | Options |
|-----------|---------|
| Kubernetes | Azure AKS / Google GKE / Oracle OKE |
| Kafka | Redpanda Cloud / Confluent Cloud / Self-hosted |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |
| Logging | ELK Stack / Cloud-native |

## Architecture Evolution

### Before Phase V (Monolithic)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│  Backend    │────▶│  Neon DB    │
│  (Next.js)  │     │  (FastAPI)  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### After Phase V (Event-Driven Microservices)
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER (AKS/GKE/OKE)                         │
│                                                                                       │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────────────────────┐ │
│  │  Frontend   │   │  Chat API   │   │              KAFKA CLUSTER                  │ │
│  │  + Dapr     │──▶│  + MCP      │──▶│  ┌─────────────┐  ┌─────────────────────┐  │ │
│  │  Sidecar    │   │  + Dapr     │   │  │ task-events │  │ reminders           │  │ │
│  └─────────────┘   └──────┬──────┘   │  └─────────────┘  └─────────────────────┘  │ │
│                           │          └──────────┬────────────────────┬────────────┘ │
│                           │                     │                    │              │
│                           ▼                     ▼                    ▼              │
│                    ┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐     │
│                    │   Neon DB   │   │ Recurring Task  │   │  Notification   │     │
│                    │  (External) │   │    Service      │   │    Service      │     │
│                    └─────────────┘   │  + Dapr Sidecar │   │  + Dapr Sidecar │     │
│                                      └─────────────────┘   └─────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `task-events` | Chat API (MCP Tools) | Recurring Task Service, Audit Service | All task CRUD operations |
| `reminders` | Chat API (when due date set) | Notification Service | Scheduled reminder triggers |
| `task-updates` | Chat API | WebSocket Service | Real-time client sync |

## Dapr Building Blocks Used

| Building Block | Use Case |
|----------------|----------|
| **Pub/Sub** | Kafka abstraction - publish/subscribe without Kafka client code |
| **State Management** | Conversation state, task caching |
| **Service Invocation** | Frontend → Backend with retries, mTLS |
| **Jobs API** | Scheduled reminders at exact times |
| **Secrets Management** | API keys, DB credentials |

## New Services

### 1. Notification Service
- Consumes from `reminders` topic
- Sends push notifications / emails when reminders trigger
- Dapr sidecar for Kafka abstraction

### 2. Recurring Task Service
- Consumes from `task-events` topic
- Creates next occurrence when recurring task completed
- Dapr sidecar for Kafka abstraction

### 3. WebSocket Service (Optional)
- Consumes from `task-updates` topic
- Broadcasts changes to connected clients
- Real-time sync across devices

## Cloud Provider Options

### Azure AKS
- $200 free credits for 30 days
- 12 months of selected free services
- Best integration with Azure DevOps

### Google GKE
- $300 free credits for 90 days
- Autopilot mode for simplified management
- Best for GCP ecosystem

### Oracle OKE (Recommended)
- **Always Free** tier (4 OCPUs, 24GB RAM)
- No credit card charge after trial
- Best for learning without time pressure

## Kafka Provider Options

### Redpanda Cloud (Recommended)
- Free Serverless tier
- Kafka-compatible API
- No Zookeeper dependency

### Self-Hosted (Strimzi)
- Free (just compute cost)
- Full control
- Good learning experience

### Confluent Cloud
- $400 credit for 30 days
- Industry standard
- Credit expires

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Advanced features work | Create recurring task, set due date, add priority/tags |
| Kafka events published | Events appear in topic on task operations |
| Dapr integration | Services communicate via Dapr sidecars |
| Cloud deployment | App accessible via cloud Kubernetes |
| CI/CD pipeline | Auto-deploy on git push |
| Monitoring | Prometheus metrics visible in Grafana |

## Implementation Order

1. **Database Schema Updates** - Add columns for new features
2. **Backend API Updates** - CRUD for new fields
3. **Frontend UI Updates** - Forms for new features
4. **Kafka Integration** - Event publishing
5. **Dapr Setup** - Sidecars and components
6. **Notification Service** - New microservice
7. **Recurring Task Service** - New microservice
8. **Local Minikube Testing** - Full stack locally
9. **Cloud Deployment** - AKS/GKE/OKE
10. **CI/CD Pipeline** - GitHub Actions
11. **Monitoring Setup** - Prometheus + Grafana

## Related Specs

- [Advanced Features Spec](./features/advanced-features.md)
- [Database Schema Updates](./features/database-schema.md)
- [Kafka Architecture](./infrastructure/kafka.md)
- [Dapr Integration](./infrastructure/dapr.md)
- [Cloud Deployment](./infrastructure/cloud-deployment.md)
- [CI/CD Pipeline](./infrastructure/cicd.md)
- [Implementation Tasks](./tasks.md)
