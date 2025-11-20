import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from faker import Faker
from uuid import uuid4

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils import get_password_hash

# 1. Setup an in-memory SQLite database for instant, clean tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
fake = Faker()

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database for every single test case.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a TestClient that uses the override database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

# --- NEW FIXTURES ADDED BELOW ---

@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Creates a single user in the database and returns it.
    """
    user_data = {
        "id": uuid4(),
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "Password123!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "is_active": True,
        "is_verified": False
    }
    # Manually hash and set using the correct model attribute
    user = User(**user_data)
    # FIX: Use 'password' column directly or 'hashed_password' logic if using init
    user.password = get_password_hash(user_data["password"]) 
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def seed_users(db_session):
    """
    Creates 5 users in the database.
    """
    users = []
    for _ in range(5):
        user_data = {
            "id": uuid4(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": "Password123!",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "is_active": True,
            "is_verified": False
        }
        user = User(**user_data)
        # FIX: Update the password field directly
        user.password = get_password_hash(user_data["password"])
        
        db_session.add(user)
        users.append(user)
    db_session.commit()
    return users