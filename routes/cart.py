from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from core.database import get_db
from core.deps import get_current_user
from models.cart import Cart, CartItem
from models.product import Product
from models.user import User
from models.order import Order, OrderItem
from schemas.cart import AddCartItemRequest, CartLineResponse, CartResponse
from schemas.order import OrderDetailResponse, OrderItemResponse

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

def build_cart_response(db, cart: Cart) -> CartResponse:
    
    lines = db.scalars(
        select(CartItem).where(CartItem.cart_id == cart.id)
    ).all()

    items: list[CartLineResponse] = []
    total = Decimal("0")

    for line in lines:
        product = db.get(Product, line.product_id)

        if product is None:
            continue

        unit = product.price
        line_total = unit * line.quantity
        total += line_total

        items.append(
            CartLineResponse( 
                product_id=product.id,
                product_name=product.name,
                quantity=line.quantity,
                unit_price=unit,
                line_total=line_total
            )
        )

    return CartResponse(
        cart_id=cart.id,
        items=items,
        total=total
    )


@router.get("", response_model=CartResponse)
def read_my_cart(
    user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    
    cart = get_or_create_cart(db, user.id)
    return build_cart_response(db, cart)

@router.post("/items", response_model=CartResponse)
def add_cart_item(
    body: AddCartItemRequest,
    user: User = Depends(get_current_user),
    db=Depends(get_db) 
):
    
    product = db.get(Product, body.product_id)
    if product is None or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    cart = get_or_create_cart(db,user.id) # 10
    
    existingCart= db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id, #10
            CartItem.product_id == body.product_id #20
        )
    )
    
    if existingCart:
        existingCart.quantity += body.quantity
    else:
        db.add(
            CartItem(
                cart_id= cart.id,
                product_id= body.product_id,
                quantity= body.quantity
            )
        )
    
    db.commit()
    db.refresh(cart)
    
    return build_cart_response(db,cart)
    
@router.delete("/items/{product_id}", response_model=CartResponse)
def remove_cart_item(
    product_id: int,
    user: User = Depends(get_current_user),
    db= Depends(get_db)
):
    
    cart = get_or_create_cart(db, user.id)
    
    isProductInCart = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )
    
    if isProductInCart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="That product is not in your cart")
    
    db.delete(isProductInCart)
    db.commit()
    db.refresh(cart)
    return build_cart_response(db,cart)
    
    
@router.post("/checkout", response_model=OrderDetailResponse)
def checkout_cart(
    user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    
    cart = get_or_create_cart(db, user.id)
    cart_items = db.scalars(
        select(CartItem).where(
            CartItem.cart_id == cart.id
        )).all()
    
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your cart is empty")
    
    total = Decimal("0")
    
    for cart_item in cart_items:
        product = db.get(Product, cart_item.product_id)
        
        if product is None or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product id {cart_item.product_id} is not available"
            )
        
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for: {product.name}"
            )
        
        total += product.price * cart_item.quantity
        
        order = Order(
            user_id= user.id,
            status="pending",
            total=total
        )
        
        db.add(order)
        db.flush()
        
    for cart_item in cart_items:
        product = db.get(Product, cart_item.product_id)

        if product is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product missing during checkout")
        
        db.add(
            OrderItem(
                order_id=order.id,
                product_id= product.id,
                quantity=cart_item.quantity,
                unit_price=product.price
            )
        )
        
        product.stock -= cart_item.quantity
        db.delete(cart_item)
        
    
    db.commit()
    db.refresh(order)
    
    order_items = db.scalars(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()
    
    items_out =[
        OrderItemResponse(
            product_id=oi.product_id,
            quantity=oi.quantity,
            unit_price=oi.unit_price,
            line_total=oi.unit_price * oi.quantity, 
        )
        
        for oi in order_items
    ]
        
    return OrderDetailResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=items_out,
    )
    