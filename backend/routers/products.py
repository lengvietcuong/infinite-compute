from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from database.database import get_db
from database.models import Product, Review, User, OrderItem, Order, OrderStatus
from schemas import ProductResponse, ProductCreate, ProductUpdate
from auth import get_current_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    architecture: Optional[str] = None,
    product_line: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all products with optional filters"""
    query = select(Product)
    
    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Product.name.ilike(search_pattern)) |
            (Product.description.ilike(search_pattern))
        )
    
    if architecture:
        query = query.where(Product.architecture == architecture)
    
    if product_line:
        query = query.where(Product.product_line == product_line)
    
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    
    if in_stock is True:
        query = query.where(Product.stock_quantity > 0)
    
    query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Add review statistics
    products_with_stats = []
    for product in products:
        product_dict = ProductResponse.model_validate(product).model_dump()
        
        # Get average rating and review count
        review_stats = await db.execute(
            select(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            ).where(Review.product_id == product.id)
        )
        stats = review_stats.first()
        
        product_dict['average_rating'] = float(stats.avg_rating) if stats.avg_rating else None
        product_dict['review_count'] = stats.review_count
        
        products_with_stats.append(ProductResponse(**product_dict))
    
    return products_with_stats


@router.get("/top-selling", response_model=List[ProductResponse])
async def get_top_selling_products(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get top selling products based on order quantities"""
    query = (
        select(Product)
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.status != OrderStatus.CANCELLED)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    # If we don't have enough best sellers, fill with other products
    if len(products) < limit:
        existing_ids = [p.id for p in products]
        remaining = limit - len(products)
        
        fallback_query = select(Product)
        if existing_ids:
            fallback_query = fallback_query.where(Product.id.not_in(existing_ids))
            
        fallback_query = fallback_query.order_by(Product.created_at.desc()).limit(remaining)
        fallback_result = await db.execute(fallback_query)
        fallback_products = fallback_result.scalars().all()
        products.extend(fallback_products)
    
    # Add review statistics
    products_with_stats = []
    for product in products:
        product_dict = ProductResponse.model_validate(product).model_dump()
        
        # Get average rating and review count
        review_stats = await db.execute(
            select(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            ).where(Review.product_id == product.id)
        )
        stats = review_stats.first()
        
        product_dict['average_rating'] = float(stats.avg_rating) if stats.avg_rating else None
        product_dict['review_count'] = stats.review_count
        
        products_with_stats.append(ProductResponse(**product_dict))
    
    return products_with_stats


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific product by ID"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get review statistics
    review_stats = await db.execute(
        select(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).where(Review.product_id == product.id)
    )
    stats = review_stats.first()
    
    product_dict = ProductResponse.model_validate(product).model_dump()
    product_dict['average_rating'] = float(stats.avg_rating) if stats.avg_rating else None
    product_dict['review_count'] = stats.review_count
    
    return ProductResponse(**product_dict)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Create a new product (Admin only)"""
    # Check if product with same name exists
    result = await db.execute(select(Product).where(Product.name == product_data.name))
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )
    
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    product_dict = ProductResponse.model_validate(new_product).model_dump()
    product_dict['average_rating'] = None
    product_dict['review_count'] = 0
    
    return ProductResponse(**product_dict)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update a product (Admin only)"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    # Get review statistics
    review_stats = await db.execute(
        select(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).where(Review.product_id == product.id)
    )
    stats = review_stats.first()
    
    product_dict = ProductResponse.model_validate(product).model_dump()
    product_dict['average_rating'] = float(stats.avg_rating) if stats.avg_rating else None
    product_dict['review_count'] = stats.review_count
    
    return ProductResponse(**product_dict)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a product (Admin only)"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    await db.delete(product)
    await db.commit()
    
    return None
