import pytest
from pydantic import ValidationError

# Import from our new, correct locations
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