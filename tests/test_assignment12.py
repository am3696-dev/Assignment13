import pytest
from fastapi.testclient import TestClient

def test_create_user(client):
    """Test that a new user can be registered."""
    # FIX: Endpoint is /auth/register, not /users/register
    response = client.post(
        "/auth/register",
        json={
            "email": "test_assign@example.com", 
            "username": "test_assign", 
            "password": "password123",
            "first_name": "Test",
            "last_name": "Assign"
        }
    )
    assert response.status_code == 201

def test_login_user(client):
    """Test that a registered user can log in."""
    # 1. Register
    client.post(
        "/auth/register",
        json={
            "email": "login_assign@example.com", 
            "username": "login_assign", 
            "password": "password123",
            "first_name": "Test",
            "last_name": "Login"
        }
    )
    
    # 2. Login (FIX: Endpoint is /auth/login)
    response = client.post(
        "/auth/login",
        json={"username": "login_assign", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    """Test that login fails with wrong password."""
    response = client.post(
        "/auth/login",
        json={"username": "wrong_user", "password": "wrongpassword"}
    )
    # FastAPI security usually returns 401 for bad auth
    assert response.status_code == 401

def test_calculation_lifecycle(client):
    """
    Test the full lifecycle: Register -> Login -> Add -> Read -> Update -> Delete
    """
    # 1. Register & Login to get Token
    client.post("/auth/register", json={
        "email": "calc_user@example.com", 
        "username": "calc_user", 
        "password": "password123",
        "first_name": "Calc", 
        "last_name": "User"
    })
    login_res = client.post("/auth/login", json={"username": "calc_user", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Calculation (Add)
    # FIX: Use "addition" (lowercase) and list inputs
    payload = {"type": "addition", "inputs": [10, 5]}
    create_res = client.post("/calculations", json=payload, headers=headers)
    assert create_res.status_code == 201
    calc_id = create_res.json()["id"]

    # 3. Read Calculation
    read_res = client.get(f"/calculations/{calc_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["result"] == 15.0

    # 4. Update Calculation
    update_res = client.put(f"/calculations/{calc_id}", json={"inputs": [10, 10]}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["result"] == 20.0  # 10 + 10

    # 5. Delete Calculation
    del_res = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert del_res.status_code == 204