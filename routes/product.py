from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func

from core.database import get_db
from core.deps import require_admin
from models.product import Product
from models.user import User

from schemas.product import ProductCreate, ProductResponse, ProductListResponse, ProductUpdate

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

@router.get("", response_model=ProductListResponse)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: str | None = None,
    search: str | None = None,
    db= Depends(get_db)
):
    query = select(Product).where(Product.is_active == True)
    
    if category:
        query = query.where(Product.category == category.strip())
        
    if search:
        query = query.where(Product.name.ilike(f"%{search.strip()}%"))
        
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(Product.id).offset(skip).limit(limit)).all()
    
    return ProductListResponse(items=rows, total=total, skip=skip, limit=limit)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    body: ProductUpdate,
    _admin: User = Depends(require_admin),
    db= Depends(get_db) 
):
    product = db.get(Product, product_id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product.name = body.name.strip()
    product.description = body.description.strip() if body.description else None
    product.price = body.price
    product.stock = body.stock
    product.category = body.category.strip() if body.category else None
    product.is_active = body.is_active
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    _admin: User = Depends(require_admin),
    db = Depends(get_db)  
):
    
    product = db.get(Product, product_id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    return {"message" : "Product deleted successfully"}
    
    