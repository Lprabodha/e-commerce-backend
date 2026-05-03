from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy import select

from core.database import get_db
from core.security import create_access_token, hash_password, verify_password

from models.user import User
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

# /auth/register
# /auth/login

@router.post("/register", response_model=UserResponse)
def register(body: RegisterRequest, db=Depends(get_db)):
    if "@" not in body.email or "." not in body.email.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email"
        )
        
    existing_email = db.scalar(select(User).where(User.email == body.email.lower()))
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered"
        )
        
    