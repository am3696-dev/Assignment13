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
    Example: inputs=[10, 5], type="subtraction" -> 10 - 5 = 5
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
    # This allows [10, 5, 2] -> (10 - 5) - 2 = 3
    try:
        result = reduce(operation_func, inputs)
        return result
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero")