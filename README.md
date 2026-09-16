# DevOps Django API

Microservicio backend desarrollado con **Django REST Framework**, diseñado como entorno de referencia para arquitecturas orientadas a eventos y flujos de infraestructura moderna.

### Stack Técnico
* **Backend:** Python 3.12, Django 5.x, Django REST Framework, Gunicorn.
* **Procesamiento Asíncrono:** Celery, RabbitMQ (Message Broker), Redis (Result Backend).
* **Contenedores & Proxy:** Docker, Docker Compose, Nginx.
* **Observabilidad:** Métricas expuestas para Prometheus y recolección de logs con Grafana Alloy / Loki.
* **Infraestructura & CI/CD:** Manifiestos listos para Kubernetes, pipelines en GitHub Actions / Jenkins y aprovisionamiento con Terraform.