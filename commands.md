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