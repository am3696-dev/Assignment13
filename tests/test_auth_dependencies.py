# tests/test_auth_dependencies.py

from uuid import uuid4
from app.auth import dependencies
from app.models.user import User
from app.schemas.user import UserResponse
from fastapi import HTTPException

# Mock database session
class FakeDB:
    def __init__(self, user):
        self.user = user

    def query(self, model):
        return self

    def filter(self, condition):
        return self

    def first(self):
        return self.user


def test_get_current_user_success(monkeypatch):
    """Test successful retrieval of current user."""
    fake_user = User(
        id=uuid4(),
        username="johndoe",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        is_active=True,
        is_verified=True,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00"
    )

    monkeypatch.setattr(User, "verify_token", lambda token: fake_user.id)
    db = FakeDB(fake_user)

    user_response = dependencies.get_current_user(db, token="fake-token")

    assert isinstance(user_response, UserResponse)
    assert user_response.id == fake_user.id
    assert user_response.username == fake_user.username
    assert user_response.email == fake_user.email


def test_get_current_user_invalid_token(monkeypatch):
    """Test retrieval with an invalid token."""
    monkeypatch.setattr(User, "verify_token", lambda token: None)
    db = FakeDB(None)

    try:
        dependencies.get_current_user(db, token="invalid-token")
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Could not validate credentials"


def test_get_current_user_not_found(monkeypatch):
    """Test retrieval when user does not exist in DB."""
    fake_id = uuid4()
    monkeypatch.setattr(User, "verify_token", lambda token: fake_id)
    db = FakeDB(None)

    try:
        dependencies.get_current_user(db, token="fake-token")
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Could not validate credentials"


def test_get_current_active_user_success(monkeypatch):
    """Test retrieval of an active user."""
    fake_user = User(
        id=uuid4(),
        username="johndoe",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        is_active=True,
        is_verified=True,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00"
    )

    monkeypatch.setattr(User, "verify_token", lambda token: fake_user.id)
    db = FakeDB(fake_user)

    current_user = dependencies.get_current_active_user(
        current_user=dependencies.get_current_user(db, token="fake-token")
    )

    assert isinstance(current_user, UserResponse)
    assert current_user.is_active is True


def test_get_current_active_user_inactive(monkeypatch):
    """Test retrieval of an inactive user raises exception."""
    fake_user = User(
        id=uuid4(),
        username="johndoe",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        is_active=False,
        is_verified=True,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00"
    )

    monkeypatch.setattr(User, "verify_token", lambda token: fake_user.id)
    db = FakeDB(fake_user)

    try:
        dependencies.get_current_active_user(
            current_user=dependencies.get_current_user(db, token="fake-token")
        )
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "Inactive user"
