from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Union, Any

# --- CONFIGURATION ---
# In a real job, these go in a .env file. For this assignment, it's okay here.
SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET_STRING"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- PASSWORD LOGIC (Your existing code) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a raw password against a stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a secure hash from a raw password.
    """
    return pwd_context.hash(password)

# --- JWT TOKEN LOGIC (New additions) ---
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None):
    """
    Creates a JWT token with an expiration time.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt