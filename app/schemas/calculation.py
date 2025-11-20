from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class CalculationType(str, Enum):
    """Valid calculation types"""
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

class CalculationBase(BaseModel):
    type: CalculationType = Field(
        ...,
        description="Type of calculation (addition, subtraction, multiplication, division)",
        example="addition"
    )
    inputs: List[float] = Field(
        ...,
        description="List of numeric inputs for the calculation",
        example=[10.5, 3, 2],
        min_items=2
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v):
        allowed = {e.value for e in CalculationType}
        if not isinstance(v, str) or v.lower() not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(sorted(allowed))}")
        return v.lower()

    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, v):
        if not isinstance(v, list):
            raise ValueError("Input should be a valid list")
        return v

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationBase":
        """Validate inputs based on calculation type"""
        if len(self.inputs) < 2:
            raise ValueError("At least two numbers are required for calculation")
        if self.type == CalculationType.DIVISION:
            # Prevent division by zero (skip the first value as numerator)
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self

    model_config = ConfigDict(from_attributes=True)

class CalculationCreate(CalculationBase):
    """Schema for creating a new Calculation"""
    user_id: UUID = Field(..., description="UUID of the user who owns this calculation")

class CalculationUpdate(BaseModel):
    """Schema for updating an existing Calculation"""
    inputs: Optional[List[float]] = Field(None, min_items=2)

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationUpdate":
        if self.inputs is not None and len(self.inputs) < 2:
            raise ValueError("At least two numbers are required for calculation")
        return self

    model_config = ConfigDict(from_attributes=True)

class CalculationResponse(CalculationBase):
    """Schema for reading a Calculation from the database"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    result: float

    model_config = ConfigDict(from_attributes=True)