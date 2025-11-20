from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Calculation
from app.schemas import CalculationCreate, CalculationRead

router = APIRouter(
    prefix="/calculations",
    tags=["Calculations"]
)

# 1. BROWSE (Get All)
@router.get("/", response_model=List[CalculationRead])
def get_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).all()

# 2. READ (Get One)
@router.get("/{id}", response_model=CalculationRead)
def get_calculation(id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == id).first()
    
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Calculation not found"
        )
    return calc

# 3. ADD (Create)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CalculationRead)
def create_calculation(calc: CalculationCreate, db: Session = Depends(get_db)):
    # Create the model instance
    new_calc = Calculation(**calc.dict())
    
    # Add to DB
    db.add(new_calc)
    db.commit()
    db.refresh(new_calc)
    
    return new_calc

# 4. EDIT (Update)
@router.put("/{id}", response_model=CalculationRead)
def update_calculation(id: int, updated_calc: CalculationCreate, db: Session = Depends(get_db)):
    query = db.query(Calculation).filter(Calculation.id == id)
    calc = query.first()
    
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Calculation not found"
        )
    
    # Update the record
    query.update(updated_calc.dict(), synchronize_session=False)
    db.commit()
    
    # Return the updated record
    return query.first()

# 5. DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(id: int, db: Session = Depends(get_db)):
    query = db.query(Calculation).filter(Calculation.id == id)
    
    if not query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Calculation not found"
        )
    
    query.delete(synchronize_session=False)
    db.commit()
    
    return # Returns 204 No Content