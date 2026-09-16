# Check Health API
curl http://localhost/api/v1/health/

# Check RabbitMQ + Celery + Redis
curl -X POST http://localhost/api/v1/task/

# Check
curl -s http://localhost/metrics | head -n 20

# DevOps Django API

Production-grade, event-driven REST API built with **Django REST Framework**, containerized with **Docker**, and engineered for high-throughput asynchronous execution, robust proxying, and real-time observability.

---

## System Architecture

The service adheres to a decoupled, event-driven pattern designed to isolate long-running workloads, guarantee consistent performance, and provide native observability hooks.

```text
[ Client / Frontend ]
         │ (HTTP :80)
         ▼
     [ Nginx ] (Reverse Proxy & Static Router)
         │ (Internal HTTP :8000)
         ▼
    [ Gunicorn ] (WSGI HTTP Application Server)
         │
    [ Django DRF ] ─────────────┬─────────────► [ Prometheus ] (Scrapes /metrics)
         │                      │
         ▼ (Publishes Tasks)    ▼ (Session / Cache Store)
    [ RabbitMQ ]             [ Redis ]
         │                      ▲
         ▼ (Consumes Tasks)     │ (Stores Task Results)
  [ Celery Worker ] ────────────┘


# RabbitMQ
http://localhost:15672 (website --> guest:guest)

# Run PyTests
docker compose exec web pytest
pytest

# Create github workflow
mkdir -p .github/workflows
touch .github/workflows/ci.yml

### Continuous Integration & Testing Layer

* **Pytest (`pytest-django`):** Framework for executing automated unit and integration tests against API endpoints and metrics routes. Uses isolated API test clients and mocks Celery task dispatchers (`delay()`) to validate request lifecycles without requiring external message broker state during test runs.
* **GitHub Actions:** Native CI automation engine triggered on code pushes and pull requests targeting the main branches. Executes a two-stage matrix pipeline:
  1. **Test Stage:** Boots an isolated Python runner, installs cached dependencies, and validates API integrity via `pytest`.
  2. **Container Build Stage:** Leverages `Docker Buildx` to verify that the multi-stage `Dockerfile` compiles cleanly into an immutable image without caching issues or broken dependencies.


### Extended Observability & Telemetry Pipeline

* **Prometheus Server:** Centralized metrics scraper querying the Nginx reverse proxy on a 5-second interval. Ingests raw Python runtime and HTTP distribution metrics exposed by `django-prometheus`.
* **Loki:** Horizontally scalable, highly available log aggregation engine inspired by Prometheus. Indexes metadata labels instead of full text content to optimize storage and query speed.
* **Grafana Alloy:** Next-generation OpenTelemetry and Prometheus-compatible telemetry collector. Hooks directly into `/var/run/docker.sock` to capture stdout/stderr streams from all cluster containers and forward structured logs to Loki.
* **Grafana:** Central telemetry dashboard provisioned with automated Prometheus and Loki datasources. Enables real-time correlation between HTTP traffic spikes (metrics) and runtime error traces (logs).


# Grafana (admin:admin)
http://localhost:3000


* **Alertmanager:** Handles alert routing, grouping, and deduplication for notifications triggered by Prometheus rules. Ingests threshold breaches (such as health-check failures or API downtime defined in `alerts.yml`) and handles notification lifecycles, silencing windows, and dispatching to on-call receivers.

# Inside kind
docker exec -it devops-cluster-control-plane crictl ps