import pytest
from uuid import uuid4
from pydantic import ValidationError

# Import the correct classes
from app.schemas.calculation import CalculationCreate, CalculationType
from app.operations.calculation_logic import perform_calculation

# --- Unit Tests ---

def test_calculation_factory():
    """
    Unit test for the calculation logic factory.
    Now expects a LIST of numbers and the "addition" style strings.
    """
    # We pass a list [10, 5]
    assert perform_calculation([10, 5], CalculationType.ADDITION.value) == 15
    assert perform_calculation([10, 5], CalculationType.SUBTRACTION.value) == 5
    assert perform_calculation([10, 5], CalculationType.MULTIPLICATION.value) == 50
    assert perform_calculation([10, 5], CalculationType.DIVISION.value) == 2.0

def test_schema_valid_creation():
    """
    Tests creating a valid Pydantic model.
    """
    data = {
        "type": "addition",       # Matches CalculationType.ADDITION
        "inputs": [10, 5],        # Matches List[float]
        "user_id": uuid4()
    }
    
    calc_schema = CalculationCreate(**data)
    
    assert calc_schema.type == CalculationType.ADDITION
    assert calc_schema.inputs == [10, 5]

def test_schema_division_by_zero():
    """
    Tests that the schema validator catches division by zero.
    """
    data = {
        "type": "division",
        "inputs": [10, 0], # Zero is the second number
        "user_id": uuid4()
    }
    
    # This should now raise a ValidationError because your Schema 
    # explicitly checks for zero in the @model_validator
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    
    assert "Cannot divide by zero" in str(exc_info.value)