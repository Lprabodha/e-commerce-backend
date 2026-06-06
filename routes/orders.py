from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from core.database import get_db
from core.deps import get_current_user, require_admin
from models.order import Order, OrderItem
from models.user import User
from schemas.order import (
    OrderDetailResponse,
    OrderItemResponse,
    OrderStatusUpdate,
    OrderSummaryResponse
)

router = APIRouter(prefix="/orders", tags=["Orders"])

NEXT_STATUS = {
    "pending" : ["paid", "cancelled"],
    "paid" : ["shipped", "cancelled"],
    "shipped" : ["delivered"],
    "delivered" : [],
    "cancelled" : []
}


@router.get("/me", response_model=list[OrderSummaryResponse])
def list_my_orders(
    user: User = Depends(get_current_user), 
    db=Depends(get_db)
):
    
    orders = db.scalars(
        select(Order)
        .where(Order.user_id == user.id)
        .order_by(Order.id.desc())
    ).all()
    
    return orders


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    
    order = db.get(Order, order_id)
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
    
    order_items = db.scalars(
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
    ).all()
    
    items_out = [
        OrderItemResponse(
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            line_total=order.unit_price * order.quantity
        )
        
        for order in order_items
    ]
    
    return OrderDetailResponse(
        id= order.id,
        user_id=order.user_id,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=items_out
    )
    
@router.patch("/{order_id}/status", response_model=OrderSummaryResponse)
def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    _admin: User = Depends(require_admin),
    db=Depends(get_db)
):
    order = db.get(Order, order_id)
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    new_status = body.status.strip().lower()
    
    allowed = NEXT_STATUS.get(order.status, [])
    if new_status not in allowed:
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Can't go from '{order.status} to {new_status}. Allowed: {allowed}")
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order