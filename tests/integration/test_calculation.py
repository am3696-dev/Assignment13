import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
import uuid

# Import from our new, correct locations
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, OperationType
from app.operations.calculation_logic import perform_calculation

# --- Unit Tests ---

def test_calculation_factory():
    """
    Unit test for the calculation logic factory.
    """
    assert perform_calculation(10, 5, OperationType.ADD) == 15
    assert perform_calculation(10, 5, OperationType.SUBTRACT) == 5
    assert perform_calculation(10, 5, OperationType.MULTIPLY) == 50
    assert perform_calculation(10, 5, OperationType.DIVIDE) == 2

def test_schema_valid_creation():
    """
    Unit test for valid Pydantic schema creation.
    """
    data = {"a": 10, "b": 5, "type": "Add"}
    calc_schema = CalculationCreate(**data)
    assert calc_schema.a == 10
    assert calc_schema.b == 5
    assert calc_schema.type == OperationType.ADD

def test_schema_division_by_zero():
    """
    Unit test to ensure Pydantic schema validation catches
    division by zero.
    """
    data = {"a": 10, "b": 0, "type": "Divide"}
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    
    # Check that the error message is what we expect
    assert "Division by zero is not allowed" in str(exc_info.value)

# --- Integration Tests ---

# This fixture assumes you have a 'session' fixture in conftest.py
# that provides a clean, transactional database session for each test.
@pytest.fixture(scope="function")
def test_user(session: Session):
    """
    Fixture to create a dummy user in the test database,
    matching the fields in your User model.
    """
    # Use the static method from the User model to hash the password
    hashed_pass = User.hash_password("testpassword123")

    # Create a user with all required fields
    user = User(
        first_name="Test",
        last_name="User",
        email="test_calc@example.com",
        username="testuser_calc",
        password=hashed_pass, # Use the hashed password
        is_active=True,
        is_verified=True
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_create_calculation_integration(session: Session, test_user: User):
    """
    Integration test to:
    1. Create a user (via fixture).
    2. Create a CalculationCreate schema.
    3. Perform the calculation.
    4. Create a Calculation DB model.
    5. Save it to the database.
    6. Query the database to verify it was saved correctly.
    """
    
    # 1. User is created by the 'test_user' fixture
    
    # 2. Create the schema
    calc_data = CalculationCreate(a=20, b=10, type=OperationType.DIVIDE)
    
    # 3. Perform the calculation (as our app logic would)
    result = perform_calculation(calc_data.a, calc_data.b, calc_data.type)
    assert result == 2.0
    
    # 4. Create the Calculation DB model
    db_calculation = Calculation(
        a=calc_data.a,
        b=calc_data.b,
        type=calc_data.type.value, # Store the string value
        result=result,
        owner_id=test_user.id # Link to the user (this is a UUID)
    )
    
    # 5. Save to the database
    session.add(db_calculation)
    session.commit()
    session.refresh(db_calculation)
    
    # 6. Query to verify
    assert db_calculation.id is not None
    assert isinstance(db_calculation.id, uuid.UUID) # Check that it is a UUID
    assert db_calculation.a == 20
    assert db_calculation.b == 10
    assert db_calculation.type == "Divide"
    assert db_calculation.result == 2.0
    
    # Verify the foreign key and relationship
    assert db_calculation.owner_id == test_user.id
    assert db_calculation.owner.username == "testuser_calc"