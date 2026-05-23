from decimal import Decimal
from pydantic import BaseModel, Field

class AddCartItemRequest(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1, default=1)
    
class CartLineResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    
class CartResponse(BaseModel):
    cart_id: int
    items: list[CartLineResponse]
    total: Decimal
    