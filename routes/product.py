from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from core.database import get_db
from core.deps import require_admin
from models.product import Product
from models.user import User

from schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    body: ProductCreate,
    _admin: User = Depends(require_admin),
    db= Depends(get_db)
):
    
    product = Product(
        name=body.name.strip(),
        description=body.description.strip() if body.description else None,
        price=body.price,
        stock=body.stock,
        category=body.category.strip() if body.category else None,
        is_active=body.is_active,
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db=Depends(get_db)):
    
    product = db.get(Product, product_id)
    
    if product is None or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product