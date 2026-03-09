<img width="1024" height="1536" alt="ChatGPT Image Mar 9, 2026, 10_14_27 PM" src="https://github.com/user-attachments/assets/2966fe75-bf39-4ceb-86e0-c6abb256923f" />**Incident Triage Backend System**

A backend service for automated incident classification, triage, and escalation designed for integration with monitoring pipelines and workflow automation tools.

The system receives incident events, applies rule-based and AI-assisted classification, enforces a strict incident lifecycle, and routes alerts through an external automation layer.

This project demonstrates a production-style architecture for reliable incident processing and alert routing.

**Overview**
Modern monitoring systems generate large volumes of alerts. Without structured triage, teams experience:

● alert fatigue
● duplicate incidents
●inconsistent severity classification
●lack of traceability in incident handling

This service acts as an incident decision engine between monitoring systems and notification channels.

It provides:

● reliable ingestion of incident events

● deterministic and AI-assisted classification

● strict lifecycle state management

● automated escalation of critical incidents

● observable system metrics

● integration with automation tools for notification delivery

**System Architecture**
              <img width="488" height="1507" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/7877dc3c-6941-42d3-acfc-127405f9d6f4" />


The backend service acts as the decision layer, while n8n handles external orchestration and notification routing.

**System Flow**
1. Monitoring system detects anomaly
2. Event is forwarded to the backend API
3. Incident payload is validated and stored
4. Deduplication prevents duplicate incidents
5. Rule engine attempts severity classification
6. If rules do not match → AI classifier is used
7. Confidence guardrail validates AI output
8. Incident state transitions are applied
9. High severity incidents trigger escalation
10. Backend emits notification webhook
11. n8n routes alerts to Slack

**Core Design Principles**
Deterministic First, AI Second

Classification follows a strict order:
                
                Rule Engine
                     ↓
                AI Classifier
                     ↓
                Fallback Severity

AI is never allowed to break the system.

**Idempotent Incident Ingestion**

Duplicate requests are prevented using an idempotency key.

POST /incidents
Header: X-Idempotency-Key

Repeated requests return the same incident record.

**Incident Deduplication**

Incidents are deduplicated using a content hash combined with a time window.

hash(title + description + source)

This prevents alert storms from repeated monitoring events.

**Incident Lifecycle State Machine**

The system enforces strict state transitions.

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

**Automatic Escalation**

Incidents classified as:

HIGH
CRITICAL

are automatically escalated and trigger external notifications.

**API Endpoints**
Create Incident
POST /incidents

Example request:

{
  "title": "Database outage",
  "description": "Primary database unreachable",
  "source": "monitoring"
}
**Get Incidents**
GET /incidents

Returns all recorded incidents.

**Incident State Transition**
PATCH /incidents/{id}/state

Moves an incident to a new lifecycle state.

**Human Override**
POST /incidents/{id}/override

Allows operators to override automated classification.

**Replay Incident**
POST /incidents/{id}/replay

Reprocesses the original incident payload.

Useful for debugging or evaluating improved classification logic.

**Metrics**
GET /metrics

Example response:

{
  "total_incidents": 12,
  "rule_classifications": 6,
  "ai_classifications": 4,
  "fallback_classifications": 2,
  "auto_escalations": 3,
  "ai_failures": 0
}

Provides observability into system behavior.

**Health Check**
GET /health

Used for service monitoring.

**Notification Pipeline**

The backend does not send notifications directly. Instead it emits a webhook event.

Backend → n8n → Slack

The n8n workflow handles:

● severity-based routing

● Slack alerts

● potential integration with email or ticketing systems

**Project Structure**
                        app
                        │
                        ├── api
                        │   └── incidents.py
                        │
                        ├── core
                        │   ├── database.py
                        │   └── metrics.py
                        │
                        ├── models
                        │   ├── incident.py
                        │   ├── audit.py
                        │   ├── idempotency.py
                        │   └── state_history.py
                        │
                        ├── schemas
                        │   └── incident.py
                        │
                        ├── services
                        │   ├── classifier.py
                        │   ├── ai_classifier.py
                        │   ├── ai_client.py
                        │   ├── notifier.py
                        │   └── state_machine.py
                        │
                        ├── utils
                        │   └── hashing.py
                        │
                        └── main.py
**Technology Stack**
Backend:Python,FastAPI
Database:SQLite,SQLModel / SQLAlchemy
Automation:n8n
Notifications:Slack API
Server:Uvicorn

**Running the Project**

Clone the repository:

git clone <repo-url>
cd Triage-Backend-System

Create virtual environment:

python -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run server:

uvicorn app.main:app --reload

Open API documentation:

http://localhost:8000/docs

**Engineering Decisions**

This project prioritizes reliability, deterministic behavior, and clear system boundaries.

FastAPI for the Backend

FastAPI was chosen for:

● high performance asynchronous request handling

● strong request validation via Pydantic

● automatic OpenAPI documentation

● suitability for microservice-style APIs

SQLite for Local Persistence

SQLite was used during development because:

● it requires no external infrastructure

● it simplifies local testing

● it allows fast iteration

The data layer is implemented using SQLModel / SQLAlchemy, allowing the system to migrate easily to PostgreSQL in production environments.

**Separation of Concerns**

The backend is intentionally designed as a decision engine, while automation and notification routing are handled externally.

Responsibilities are divided as follows:

Backend service:

incident ingestion
classification
state machine enforcement
escalation logic
audit logging
metrics

Automation layer (n8n):

alert routing
Slack notifications
workflow orchestration
external integrations

This separation keeps the backend deterministic and testable.

**AI as an Assistive Layer**

AI classification is intentionally not the primary decision system.

The classification pipeline is:

                Rule Engine
                     ↓
                AI Classification
                     ↓
                Fallback Severity

Rules handle known conditions deterministically, while AI assists with ambiguous cases.

A confidence guardrail ensures low-confidence predictions default to a safe severity level.

**Failure Handling Strategy**

The system is designed to avoid cascading failures when external systems or AI components behave unpredictably.

AI Failure Handling

If the AI classifier fails:

severity = MEDIUM
response_source = fallback

This ensures the system remains operational even when AI is unavailable.

**Idempotent Event Processing**

Incoming requests support idempotency keys.

This ensures repeated ingestion attempts do not create duplicate incidents.

**Deduplication Window**

Repeated monitoring events are deduplicated using a hash-based detection mechanism combined with a time window.

This prevents alert storms when monitoring systems repeatedly emit the same event.

**External Notification Failures**

Notification delivery is delegated to n8n, allowing retries and routing logic to be handled outside the backend service.

The backend therefore remains stateless with respect to notification delivery.

**Future Improvements**

The current implementation focuses on the core incident triage pipeline.

Potential improvements include:

Production Database

Replace SQLite with PostgreSQL for:

● concurrency

● durability

● horizontal scalability

**Incident Timeline API**

Expose a dedicated endpoint:

GET /incidents/{id}/timeline

This would provide a full chronological view of incident lifecycle events.

**Rate Limiting**

Protect ingestion endpoints from event floods using rate limiting or event queue buffering.

**Alert Deduplication for Notifications**

Extend the deduplication system to suppress repeated notifications for the same incident.

**Additional Notification Integrations**

Future integrations could include:

● PagerDuty

● Opsgenie

● Email notifications

● ticketing systems

**Observability Improvements**

Export metrics to systems such as:

Prometheus

Grafana

for long-term operational monitoring.
**●Engineering Goals**

This project focuses on:

● reliable event ingestion

● safe integration of AI classification

● deterministic system behavior

● observable incident processing

● automation-first architecture

The goal is to demonstrate how incident triage systems used by SRE teams can be designed as reliable backend services.

**Author**

Hemant Dhaker



