import operator
from functools import reduce
from app.schemas.calculation import CalculationType

# Map the new Enum to operators
CALCULATION_OPERATIONS = {
    CalculationType.ADDITION: operator.add,
    CalculationType.SUBTRACTION: operator.sub,
    CalculationType.MULTIPLICATION: operator.mul,
    CalculationType.DIVISION: operator.truediv,
}

def perform_calculation(inputs: list[float], type: str) -> float:
    """
    Performs calculation on a list of numbers.
    """
    # 1. Validate Type
    try:
        calc_type = CalculationType(type.lower())
    except ValueError:
        raise ValueError(f"Invalid calculation type: {type}")

    operation_func = CALCULATION_OPERATIONS.get(calc_type)

    if not operation_func:
        raise ValueError(f"Operation {type} not supported.")

    # 2. Perform Calculation using reduce
    try:
        result = reduce(operation_func, inputs)
        return result
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero")

# ---------------------------------------------------------
# LEGACY FUNCTIONS (Required for Unit Tests to pass)
# ---------------------------------------------------------
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!") 
    return a / b