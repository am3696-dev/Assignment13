from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.utils import hash_password, verify_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash the password using the utility function
    hashed_pwd = hash_password(user_data.password)
    
    # 3. Create User Instance
    new_user = User(email=user_data.email, password=hashed_pwd)
    
    # 4. Save to Database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login_user(user_credentials: UserCreate, db: Session = Depends(get_db)):
    # 1. Retrieve user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    # 2. Verify User exists and Password matches
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
        
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    
    # 3. Successful Login
    return {"message": "Login Successful", "user_id": user.id}