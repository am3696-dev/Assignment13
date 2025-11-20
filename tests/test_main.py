from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_health():
    """
    Test the health check endpoint.
    This ensures the API is running and accessible.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}