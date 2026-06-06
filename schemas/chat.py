from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    
    customer_message: str = Field(min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    
    reply: str