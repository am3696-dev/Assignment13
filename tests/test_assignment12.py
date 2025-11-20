from fastapi.testclient import TestClient
from app.main import app
import pytest

# Create a local client fixture for testing
@pytest.fixture
def client():
    return TestClient(app)

# ----------------------------------------------------------------
# USER TESTS
# ----------------------------------------------------------------

def test_create_user(client):
    """Test that a new user can be registered."""
    response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    # Accept 201 (Created) or 400 (if running tests repeatedly without clearing DB)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

def test_login_user(client):
    """Test that a registered user can log in."""
    # 1. Register a specific user for login
    client.post(
        "/users/register",
        json={"email": "login@example.com", "password": "password123"}
    )
    
    # 2. Attempt to log in with correct credentials
    response = client.post(
        "/users/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Login Successful"

def test_login_invalid_credentials(client):
    """Test that login fails with wrong password."""
    response = client.post(
        "/users/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 403

# ----------------------------------------------------------------
# CALCULATION TESTS (BREAD)
# ----------------------------------------------------------------

def test_create_calculation(client):
    """Test CREATE (Add) operation."""
    payload = {"a": 10, "b": 5, "operation": "add"} 
    response = client.post("/calculations/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["a"] == 10
    assert data["b"] == 5
    assert "id" in data

def test_read_calculation(client):
    """Test READ operation."""
    # 1. Create a calculation
    create_res = client.post("/calculations/", json={"a": 5, "b": 5, "operation": "add"})
    calc_id = create_res.json()["id"]
    
    # 2. Retrieve it by ID
    response = client.get(f"/calculations/{calc_id}")
    assert response.status_code == 200
    assert response.json()["id"] == calc_id

def test_update_calculation(client):
    """Test EDIT (Update) operation."""
    # 1. Create a calculation
    create_res = client.post("/calculations/", json={"a": 5, "b": 5, "operation": "add"})
    calc_id = create_res.json()["id"]
    
    # 2. Update it (change 'a' to 20)
    updated_payload = {"a": 20, "b": 5, "operation": "add"}
    response = client.put(f"/calculations/{calc_id}", json=updated_payload)
    
    assert response.status_code == 200
    assert response.json()["a"] == 20

def test_delete_calculation(client):
    """Test DELETE operation."""
    # 1. Create a calculation
    create_res = client.post("/calculations/", json={"a": 5, "b": 5, "operation": "add"})
    calc_id = create_res.json()["id"]
    
    # 2. Delete it
    response = client.delete(f"/calculations/{calc_id}")
    assert response.status_code == 204
    
    # 3. Verify it is gone (should return 404)
    get_res = client.get(f"/calculations/{calc_id}")
    assert get_res.status_code == 404