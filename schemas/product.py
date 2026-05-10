from decimal import Decimal

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price : Decimal = Field(gt=0)
    stock: int = Field(gt=0)
    category: str | None = None
    is_active: bool = True
    
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    category: str| None
    is_active : bool
    