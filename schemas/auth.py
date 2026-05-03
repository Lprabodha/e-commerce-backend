from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6, description="At least 6 characters")
    
class LoginRequest(BaseModel):
    email: str
    password: str
    
    
class TokenResponse(BaseModel):
    access_token : str
    token_type: str = "bearer"
    

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    
    model_config = {"from_attributes": True}