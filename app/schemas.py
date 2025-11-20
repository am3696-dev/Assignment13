from pydantic import BaseModel, EmailStr

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- Calculation Schemas ---
class CalculationBase(BaseModel):
    a: int
    b: int
    operation: str

class CalculationCreate(CalculationBase):
    pass

class CalculationRead(CalculationBase):
    id: int
    class Config:
        from_attributes = True