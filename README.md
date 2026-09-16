# DevOps Django API

[![CI Pipeline](https://github.com/your-username/devops-django-api/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/devops-django-api/actions)
[![Kubernetes](https://img.shields.io/badge/kubernetes-v1.30-blue.svg)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/terraform-AWS%20EKS-purple.svg)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.14-blue.svg)](https://www.python.org/)

Production-grade, event-driven REST API built with **Django REST Framework**, containerized with **Docker**, and engineered for high-throughput asynchronous execution, robust reverse-proxy routing, comprehensive telemetry, and cloud-native orchestration across **Kubernetes** and **Terraform**.

---

## Architecture Overview

The system implements a decoupled, event-driven architecture designed to isolate compute-heavy operations from the synchronous HTTP request-response cycle, backed by a unified telemetry pipeline.

```text
                                    ┌────────────────────────────────────────────────────────┐
                                    │               Observability Pipeline                   │
                                    │                                                        │
                                    │   [ cAdvisor ] ─────────┐                              │
                                    │                         ▼                              │
                                    │   [ Alloy ] ───► [ Loki ] ───► [ Grafana ]             │
                                    │     (Logs)                    (Port :3000)             │
                                    │                                    ▲                   │
                                    │   [ Prometheus ] ──────────────────┤                   │
                                    │     (Port :9090)                   ▼                   │
                                    │          │                 [ Alertmanager ]            │
                                    │          ▼                   (Port :9093)              │
                                    └──────────┼─────────────────────────────────────────────┘
                                               │
                                 Scrapes /metrics on :8000
                                               │
[ Client / Web Traffic ]                       │
          │                                    │
          │ (HTTP :80 / HTTPS :443)            │
          ▼                                    │
┌─────────────────────────┐                    │
│   Nginx Ingress / Proxy │                    │
└───────────┬─────────────┘                    │
            │                                  │
            ▼ (Proxy Pass :8000)               │
┌─────────────────────────┐                    │
│   Gunicorn (WSGI)       │                    │
│   ┌───────────────────┐ │                    │
│   │ Django REST API   ├─┴────────────────────┘
│   └─────────┬─────────┘
│             │ (Dispatches Task via AMQP :5672)
│             ▼
│       [ RabbitMQ ] (Message Broker - UI :15672)
│             │
│             │ (Pushes Task over persistent TCP)
│             ▼
│       [ Celery Worker ]
│             │
│             │ (Writes Task Result / State)
│             ▼
│         [ Redis ] (Result Backend & Key-Value Cache :6379)
└────────────────────────────────────────────────────────────┘
```

---

## Technical Stack

| Layer | Technologies | Key Functionality |
| :--- | :--- | :--- |
| **Application Runtime** | Python, Django, Django REST Framework, Gunicorn | Synchronous REST endpoints, serialization, WSGI concurrency. |
| **Asynchronous Engine** | Celery, RabbitMQ, Redis | AMQP-based message delivery, decoupled task execution, transient result caching. |
| **Gateway & Routing** | Nginx, Nginx Ingress Controller | Static asset offloading, reverse proxying, virtual host resolution. |
| **Telemetry & Metrics** | Prometheus, `django-prometheus`, cAdvisor | Time-series metric collection, scrapers, node resource tracking. |
| **Logging Pipeline** | Grafana Alloy, Grafana Loki | Container stdout/stderr harvesting via Docker socket, indexed log querying. |
| **Visualization & Alerts**| Grafana, Alertmanager | Dashboarding, metric-log correlation, threshold rule alerting. |
| **Local Orchestration** | Docker, Docker Compose, Kind (K8s-in-Docker) | Local cluster emulation, container isolation, declarative testing. |
| **Infrastructure as Code**| Terraform (AWS EKS, VPC modules) | Modular, reproducible cloud infrastructure provisioning. |
| **CI/CD Automation** | GitHub Actions, Pytest (`pytest-django`) | Automated test runs, Docker Buildx image validation. |

---

## Repository Layout

```text
.
├── .github/workflows/ci.yml       # Two-stage CI matrix (Pytest + Docker Buildx)
├── core/                          # Django core project configuration & WSGI/ASGI
├── k8s/                           # Declarative Kubernetes manifests
│   ├── 00-namespace.yaml          # Isolated namespace (devops-django)
│   ├── 01-configmap.yaml          # Environment configs & non-sensitive settings
│   ├── 02-secrets.yaml            # Base64 encoded operational secrets
│   ├── 03-redis-rabbitmq.yaml     # In-cluster state stores (Deployments + Services)
│   ├── 04-django-api.yaml         # Django Gunicorn API deployment + ClusterIP
│   ├── 05-celery-worker.yaml      # Async Celery execution engine deployment
│   ├── 06-ingress.yaml            # Ingress rules mapping api.local
│   └── 07-hpa.yaml                # Horizontal Pod Autoscaler (target: 70% CPU)
├── nginx/                         # Docker Compose reverse-proxy configurations
├── observability/                 # Prometheus targets, alert rules, Alloy pipelines
├── terraform/                     # Cloud provisioning templates
│   ├── main.tf                    # AWS VPC & EKS cluster module definition
│   ├── variables.tf               # Configurable deployment parameters
│   └── outputs.tf                 # EKS cluster endpoints & kubeconfig helpers
├── tests/                         # Pytest suite with Celery mocking & API tests
├── docker-compose.yml             # Local runtime with complete observability stack
├── Dockerfile                     # Multi-stage container definition
├── kind-config.yaml               # Kind local cluster config mapping ports 80/443
└── requirements.txt               # Locked project dependencies
```

---

## Deployment & Execution Modes

### Mode 1: Local Full-Stack (Docker Compose)

Best for rapid feature development and end-to-end observability testing:

```bash
# Boot the entire infrastructure in detached mode
docker compose up -d

# Verify all containers are healthy
docker compose ps
```

* **Django API:** `http://localhost/api/v1/health/`
* **Prometheus Metrics:** `http://localhost/metrics`
* **RabbitMQ Management:** `http://localhost:15672` *(Credentials: `guest` / `guest`)*
* **Grafana Dashboards:** `http://localhost:3000` *(Credentials: `admin` / `admin`)*
* **Prometheus UI:** `http://localhost:9090`
* **Alertmanager UI:** `http://localhost:9093`

---

### Mode 2: Cloud-Native Simulation (Kubernetes via Kind)

Tests declarative infrastructure locally using native Kubernetes objects:

**1. Initialize Kind Cluster with Ingress Port Mappings**
```bash
kind create cluster --name devops-cluster --config kind-config.yaml
```

**2. Deploy the Ingress-Nginx Controller**
```bash
kubectl apply -f [https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml](https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml)

# Await controller readiness
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

**3. Build and Sideload the Local Image**
```bash
docker build -t devops-django-api:latest .
kind load docker-image devops-django-api:latest --name devops-cluster
```

**4. Apply All Kubernetes Manifests**
```bash
kubectl apply -f k8s/

# Monitor deployment rollout
kubectl get pods -n devops-django -w
```

---

## Verification & API Endpoints

### 1. Health Probe
```bash
# Under Docker Compose:
curl http://localhost/api/v1/health/

# Under Kubernetes Ingress:
curl -H "Host: api.local" http://localhost/api/v1/health/
```
*Expected Output:*
```json
{"status":"healthy","service":"django-api"}
```

### 2. Async Task Dispatch (202 Accepted Pattern)
```bash
# Trigger an asynchronous job to RabbitMQ:
curl -X POST -H "Host: api.local" http://localhost/api/v1/task/
```
*Expected Output:*
```json
{"task_id":"d12b071c-3f41-4775-a83a-3453b3b42a9b","status":"enqueued"}
```

### 3. Inspect Worker Processing
```bash
# Verify worker consumed the message (Kubernetes):
kubectl logs -n devops-django -l app=celery-worker --tail=20

# Verify inner container runtimes inside the Kind node:
docker exec -it devops-cluster-control-plane crictl ps
```

### 4. Metrics Inspection
```bash
curl -s http://localhost/metrics | head -n 20
```

---

## Testing & Quality Assurance

The test suite runs with `pytest` and `pytest-django`, isolating HTTP execution from stateful infrastructure brokers:

```bash
# Run unit tests natively
pytest

# Run tests inside the running Compose container
docker compose exec web pytest
```

### Continuous Integration Matrix
On every pull request or push to `main`, GitHub Actions executes:
1. **Unit & Integration Tests:** Spin up isolated runners, inject test environments, run `pytest`, and enforce coverage thresholds.
2. **Container Build Checks:** Uses `docker/build-push-action` to ensure image compilation succeeds without caching defects.

---

## Infrastructure as Code (Terraform)

The `terraform/` directory defines an enterprise AWS deployment architecture:
* Dedicated **VPC** across 2 Availability Zones with public/private subnet segmentation.
* Single **NAT Gateway** for cost-efficient egress from private worker nodes.
* Managed **AWS EKS** cluster (`v1.30`) with an auto-scaling managed node group (`t3.medium`, 2 to 5 instances).

To validate the configuration without provisioning live cloud resources:

```bash
cd terraform
terraform init
terraform validate
terraform plan
```

---

## Tear Down & Cleanup

To free system resources and dismantle local clusters:

```bash
# Destroy Docker Compose resources and volumes
docker compose down -v

# Delete the local Kind Kubernetes cluster
kind delete cluster --name devops-cluster
```