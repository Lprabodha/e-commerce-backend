from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    
class OrderSummaryResponse(BaseModel):
    id: int
    status: str
    total: Decimal
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
class OrderDetailResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]
    
class OrderStatusUpdate(BaseModel):
    status: str =  Field(min_length=1, max_length=30)