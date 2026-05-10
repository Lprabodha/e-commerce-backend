from fastapi import APIRouter, Depends, status
from fastapi import HTTPException

from schemas.auth import UserResponse
from models.user import User
from core.database import get_db
from sqlalchemy import select

from core.deps import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_me(user:User = Depends(get_current_user)):
    return user

@router.get("/", response_model=list[UserResponse])
def list_users(_admin: User = Depends(require_admin), db=Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    
    if user.role != "admin" and user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own profile")
    
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user