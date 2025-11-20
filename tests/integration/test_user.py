import pytest
from faker import Faker
from uuid import uuid4
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

# --- CORRECT IMPORTS FROM YOUR APP STRUCTURE ---
from app.models.user import User
from app.database import Base
from app.utils import get_password_hash

# Initialize Faker
fake = Faker()

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def create_fake_user():
    """
    Helper to generate a dictionary of valid fake user data.
    """
    password = "Password123!"
    return {
        "id": uuid4(),
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "password": password,
        # We use 'hashed_password' because your User.__init__ looks for this key
        "hashed_password": get_password_hash(password), 
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "is_active": True,
        "is_verified": False
    }

@contextmanager
def managed_db_session():
    """
    Context manager that creates an isolated in-memory database session.
    Used specifically for 'test_managed_session' and 'test_error_handling'.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

# ------------------------------------------------------------------------------
# INTEGRATION TESTS
# ------------------------------------------------------------------------------

def test_managed_session():
    """
    Test the managed_db_session context manager works correctly.
    """
    with managed_db_session() as session:
        # Verify we can do a basic query (e.g. check 1=1)
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1

def test_create_user_with_faker(db_session):
    """
    Create a single user using Faker-generated data and verify it was saved.
    """
    user_data = create_fake_user()
    # Remove raw password before creating model, keep hash
    user_data.pop("password") 
    
    new_user = User(**user_data)
    db_session.add(new_user)
    db_session.commit()

    # Query back
    saved_user = db_session.query(User).filter_by(email=user_data["email"]).first()
    assert saved_user is not None
    assert saved_user.username == user_data["username"]
    # FIX: Check 'password' column, not 'password_hash'
    assert saved_user.password is not None

def test_create_multiple_users(db_session):
    """
    Create multiple users in a loop and verify they are all saved.
    """
    users = []
    for _ in range(3):
        user_data = create_fake_user()
        user_data.pop("password") 
        user = User(**user_data)
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    
    count = db_session.query(User).count()
    assert count == 3

def test_query_methods(db_session, seed_users):
    """
    Test various query methods (filter, limit, order_by) using the seed_users fixture.
    """
    # Test Count
    total_users = db_session.query(User).count()
    assert total_users == 5  # Assuming seed_users fixture creates 5 users

    # Test Filter
    first_user = seed_users[0]
    fetched_user = db_session.query(User).filter(User.email == first_user.email).first()
    assert fetched_user.id == first_user.id

    # Test Limit
    limited_users = db_session.query(User).limit(2).all()
    assert len(limited_users) == 2

def test_update_with_refresh(db_session, test_user):
    """
    Test updating a user and using refresh to get the latest data.
    """
    # Update the name
    new_name = "UpdatedName"
    test_user.first_name = new_name
    db_session.commit()
    
    # Refresh object from DB
    db_session.refresh(test_user)
    
    assert test_user.first_name == new_name

@pytest.mark.slow
def test_bulk_operations(db_session):
    """
    Test bulk inserting multiple users at once.
    """
    users_data = []
    for _ in range(10):
        u_data = create_fake_user()
        u_data.pop("password")
        users_data.append(User(**u_data))

    db_session.add_all(users_data)
    db_session.commit()
    
    assert db_session.query(User).count() == 10

def test_unique_email_constraint(db_session):
    """
    Create two users with the same email and expect an IntegrityError.
    """
    # Create first user
    data1 = create_fake_user()
    data1.pop("password")
    user1 = User(**data1)
    db_session.add(user1)
    db_session.commit()

    # Create second user with SAME email
    data2 = create_fake_user()
    data2["email"] = data1["email"] # Duplicate email
    data2.pop("password")
    user2 = User(**data2)
    
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()

def test_unique_username_constraint(db_session):
    """
    Create two users with the same username and expect an IntegrityError.
    """
    # Create first user
    data1 = create_fake_user()
    data1.pop("password")
    user1 = User(**data1)
    db_session.add(user1)
    db_session.commit()

    # Create second user with SAME username
    data2 = create_fake_user()
    data2["username"] = data1["username"] # Duplicate username
    data2.pop("password")
    user2 = User(**data2)
    
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()

def test_error_handling():
    """
    Verify that invalid SQL raises an exception.
    """
    with pytest.raises(Exception) as exc_info:
        with managed_db_session() as session:
            session.execute(text("SELECT * FROM non_existent_table"))
    
    assert "no such table" in str(exc_info.value).lower()