from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    try:
        # Convert Pydantic model to dict
        user_dict = user_data.model_dump()
        new_user = User.register(db=db, user_data=user_dict)
        db.commit()
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint. Returns JWT token + User Details in a flat structure.
    Expects JSON body: {"username": "...", "password": "..."}
    """
    # 1. Authenticate using the data from the JSON body (user_data)
    auth_result = User.authenticate(
        db=db, 
        username_or_email=user_data.username, 
        password=user_data.password
    )
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Extract the user object from the auth_result dictionary
    user = auth_result["user"]
    
    # 3. Construct the response matching your specific TokenResponse schema
    return TokenResponse(
        access_token=auth_result["access_token"],
        refresh_token=auth_result["refresh_token"],
        token_type=auth_result["token_type"],
        expires_at=auth_result["expires_at"],
        
        # Flattened User Fields
        user_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified
    )