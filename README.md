AI-Assisted Incident Triage Backend System

An automated incident triage and escalation system built using FastAPI and n8n that intelligently classifies incoming incidents, enforces a strict lifecycle state machine, and routes alerts to Slack through an automation workflow.

This system demonstrates how modern SRE / DevOps incident pipelines work in production environments.

System Overview-

Modern systems generate thousands of monitoring alerts. Without proper triage, engineers face:

>alert fatigue

>duplicate incidents

>unclear prioritization

>missing audit trails

This system solves that by creating an automated incident decision engine.

>Incoming events are processed through:

>Incident ingestion API

>Deduplication & idempotency checks

>Rule-based classification

>AI-assisted classification fallback

>Severity validation

>Incident lifecycle state machine

>Automatic escalation

>Notification routing via n8n

>Slack alerts

>Architecture

Architecture

External Monitoring Systems
        │
        ▼
      n8n Webhook
 (Event Intake Layer)
        │
        ▼
FastAPI Incident Engine
        │
        ├── Idempotency Check
        ├── Deduplication (Hash + Time Window)
        ├── Rule Engine
        ├── AI Classification
        ├── Confidence Guardrails
        ├── Incident State Machine
        ├── Escalation Logic
        └── Audit Logging
                │
                ▼
         Notification Trigger
                │
                ▼
               n8n
                │
                ▼
          Slack Alert Routing

System Flow:

1. Monitoring system detects anomaly
2. Event sent to n8n webhook
3. n8n forwards payload to backend API
4. Backend validates payload
5. Deduplication + idempotency checks
6. Rule engine attempts classification
7. If rules fail → AI classifier
8. Severity determined
9. Incident state transitions applied
10. High severity incidents escalated
11. Backend triggers notification webhook
12. n8n routes alert to Slack channels

Tech Stack

Backend:

>FastAPI

>Python

Database:

>SQLite

>SQLModel / SQLAlchemy

Automation:

>n8n workflow engine

Notifications:

>Slack API

Server:

>Uvicorn

Key Features
Incident Ingestion

POST /incidents

Accepts monitoring events and stores them as incidents.

Supports:

idempotency keys

payload validation

raw payload storage

Deduplication

Incidents are deduplicated using:

SHA256 hash of incident content
+ time window validation

Prevents duplicate alerts.

                Classification Pipeline
                Rule Engine
                    ↓
                AI Classifier
                    ↓
                Confidence Guardrail
                    ↓
                Fallback Severity

Ensures AI never breaks the system.

Incident State Machine

The system enforces strict lifecycle transitions.

                RECEIVED
                ↓
                CLASSIFIED
                ↓
                ESCALATED
                ↓
                ACKNOWLEDGED
                ↓
                RESOLVED
                ↓
                OVERRIDDEN

Invalid transitions are rejected.

Automatic Escalation

Incidents with severity:

HIGH
CRITICAL

are automatically escalated and trigger notifications.

Human Override

POST /incidents/{id}/override

Allows engineers to override AI decisions.

Replay Capability
POST /incidents/{id}/replay

Reprocesses stored incidents using original payload.

Useful for debugging and testing new classification logic.

Audit Logging

Every decision is recorded:

classification

escalation

overrides

state transitions

Ensures full traceability.

Metrics & Observability
GET /metrics

Example output:

{
  "total_incidents": 12,
  "rule_classifications": 5,
  "ai_classifications": 4,
  "fallback_classifications": 3,
  "auto_escalations": 2,
  "ai_failures": 0
}
Health Check
GET /health

Used for monitoring service availability.

Project Structure
            Triage-Backend-System
                    │
                    ├── app
                    │   ├── api
                    │   │   └── incidents.py
                    │   │
                    │   ├── core
                    │   │   ├── database.py
                    │   │   └── metrics.py
                    │   │
                    │   ├── models
                    │   │   ├── incident.py
                    │   │   ├── audit.py
                    │   │   ├── idempotency.py
                    │   │   └── state_history.py
                    │   │
                    │   ├── schemas
                    │   │   └── incident.py
                    │   │
                    │   ├── services
                    │   │   ├── classifier.py
                    │   │   ├── ai_classifier.py
                    │   │   ├── ai_client.py
                    │   │   ├── notifier.py
                    │   │   └── state_machine.py
                    │   │
                    │   ├── utils
                    │   │   └── hashing.py
                    │   │
                    │   └── main.py
                    │
                    ├── migrations
                    ├── incident.db
                    └── .gitignore

Example API Usage

Create Incident

POST /incidents
{
  "title": "Database outage",
  "description": "Primary DB unreachable",
  "source": "monitoring"
}
Slack Alert Example
🚨 CRITICAL INCIDENT

Title: Database outage
Severity: CRITICAL
Source: monitoring
Incident ID: 12345
Author

Hemant Dhaker

Project Goal

This project demonstrates how AI-assisted incident automation systems used by SRE teams can be designed using modern backend architectures.

The system emphasizes:

reliability

automation

observability

safety around AI decision making