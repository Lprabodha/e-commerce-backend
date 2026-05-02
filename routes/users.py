from fastapi import APIRouter
from fastapi import HTTPException

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users():
    
    users_list = [
        {"id": 1, "name": "Nimal"},
        {"id": 2, "name": "kamal"},
        {"id": 3, "name": "Dilan"},
    ]
    
    return users_list

@router.get("/{user_id}")
def get_user(user_id: int):
    
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid User ID")
    
    if user_id > 10:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id": user_id}

@router.post("/")
def create_user(name: str):
    return {"message": f"User {name} created"}

@router.delete("/{user_id}")
def delete_user(user_id : int):
    return {"message" : f"User {user_id} deleted"}