from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List
from database.database import get_db
from database.models import Review, Product, User, Order, OrderItem, OrderStatus
from schemas import ReviewCreate, ReviewResponse, ReviewUpdate
from auth import get_current_user, get_current_admin, get_current_staff

router = APIRouter(prefix="/reviews", tags=["Reviews"])


async def can_user_review_product(db: AsyncSession, user_id: int, product_id: int) -> bool:
    """Check if user has a shipped or delivered order containing the product"""
    result = await db.execute(
        select(Order)
        .join(OrderItem, Order.id == OrderItem.order_id)
        .where(
            and_(
                Order.user_id == user_id,
                OrderItem.product_id == product_id,
                or_(Order.status == OrderStatus.SHIPPED, Order.status == OrderStatus.DELIVERED)
            )
        )
        .limit(1)
    )
    order = result.scalar_one_or_none()
    return order is not None


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a specific product"""
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get reviews with user names
    result = await db.execute(
        select(Review, User.full_name)
        .join(User, Review.user_id == User.id)
        .where(Review.product_id == product_id)
        .offset(skip)
        .limit(limit)
        .order_by(Review.created_at.desc())
    )
    reviews_with_names = result.all()
    
    return [
        ReviewResponse(
            **review.__dict__,
            user_name=user_name
        )
        for review, user_name in reviews_with_names
    ]


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review (must have shipped order with product)"""
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == review_data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has already reviewed this product
    result = await db.execute(
        select(Review).where(
            and_(
                Review.user_id == current_user.id,
                Review.product_id == review_data.product_id
            )
        )
    )
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # Check if user can review (has shipped order with product)
    can_review = await can_user_review_product(db, current_user.id, review_data.product_id)
    
    if not can_review:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review products from your shipped or delivered orders"
        )
    
    # Create review
    new_review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    
    return ReviewResponse(
        **new_review.__dict__,
        user_name=current_user.full_name
    )


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review (own reviews only)"""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns this review
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )
    
    # Update fields
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        **review.__dict__,
        user_name=current_user.full_name
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review (own reviews or admin)"""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns this review or is admin
    from database.models import UserRole
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    await db.delete(review)
    await db.commit()
    
    return None


@router.get("", response_model=List[ReviewResponse])
async def list_all_reviews(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """List all reviews (Staff/Admin)"""
    result = await db.execute(
        select(Review, User.full_name, Product.name)
        .join(User, Review.user_id == User.id)
        .join(Product, Review.product_id == Product.id)
        .offset(skip)
        .limit(limit)
        .order_by(Review.created_at.desc())
    )
    reviews_data = result.all()
    
    return [
        ReviewResponse(
            **review.__dict__,
            user_name=user_name,
            product_name=product_name
        )
        for review, user_name, product_name in reviews_data
    ]


@router.get("/check-eligibility/{product_id}")
async def check_review_eligibility(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if user can review a product"""
    # Check if user has already reviewed this product
    result = await db.execute(
        select(Review).where(
            and_(
                Review.user_id == current_user.id,
                Review.product_id == product_id
            )
        )
    )
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        return {"can_review": False, "reason": "already_reviewed"}

    # Check if user has a shipped order with this product
    can_review = await can_user_review_product(db, current_user.id, product_id)
    
    if not can_review:
        return {"can_review": False, "reason": "no_purchase"}
        
    return {"can_review": True, "reason": None}
