from unittest.mock import patch
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

def test_health_check_endpoint(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "django-api"}

def test_prometheus_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "django_http_requests_total_by_view_transport_method_total" in response.content.decode("utf-8")

@patch("core.celery.test_async_task.delay")
def test_trigger_task_endpoint(mock_celery_delay, client):
    # Mock de la tarea de Celery para no requerir conexión real a RabbitMQ en unit tests
    mock_celery_delay.return_value.id = "mock-uuid-12345"
    
    response = client.post("/api/v1/task/")
    assert response.status_code == 202
    assert response.json() == {"task_id": "mock-uuid-12345", "status": "enqueued"}
    mock_celery_delay.assert_called_once()