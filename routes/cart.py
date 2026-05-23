from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from core.database import get_db
from core.deps import get_current_user
from models.cart import Cart, CartItem
from models.product import Product
from models.user import User
from schemas.cart import AddCartItemRequest, CartLineResponse, CartResponse

router = APIRouter(prefix="/cart", tags=["Cart"])

# GET /cart
# POST /cart/items

def get_or_create_cart(db, user_id: int) -> Cart:
    
    cart = db.scalar(select(Cart).where(Cart.user_id == user_id))
    
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    return cart

def build_cart_response(db, cart:Cart) -> CartResponse:
    
    lines = db.scalars(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    items: list[CartLineResponse] = []
    total= Decimal("0")
    
    for line in lines:
        product = db.get(Product, line.product_id)
        
        if product is None:
            continue
        
        unit = product.price
        line_total= unit * line.quantity
        total += line_total
        
        items.append(
            CartResponse(
                product_id=product.id,
                product_name=product.name,
                quantity=line.quantity,
                unit_price= unit,
                line_total= line_total
            )
        )
        
    return CartResponse(cart_id=cart.id, items=items, total=total)


@router.get("", response_model=CartResponse)
def read_my_cart(
    user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    
    cart = get_or_create_cart(db, user.id)
    return build_cart_response(db, cart)