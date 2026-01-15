from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from database.database import get_db
from database.models import Coupon, User
from auth import get_current_staff


router = APIRouter(prefix="/coupons", tags=["coupons"])


class CouponCreateRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    discount_percent: Decimal = Field(..., ge=0, le=100)
    is_active: bool = True


class CouponUpdateRequest(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=50)
    discount_percent: Decimal | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class CouponDetailResponse(BaseModel):
    id: int
    code: str
    discount_percent: Decimal
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[CouponDetailResponse])
async def get_all_coupons(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
):
    """Get all coupons with optional filters (Admin and Staff only)"""
    query = select(Coupon)
    
    if search:
        query = query.where(Coupon.code.ilike(f"%{search}%"))
    
    if is_active is not None:
        query = query.where(Coupon.is_active == is_active)
    
    query = query.order_by(Coupon.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    coupons = result.scalars().all()
    
    return [
        CouponDetailResponse(
            id=coupon.id,
            code=coupon.code,
            discount_percent=coupon.discount_percent,
            is_active=coupon.is_active,
            created_at=coupon.created_at.isoformat(),
        )
        for coupon in coupons
    ]


@router.get("/stats")
async def get_coupon_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Get coupon statistics (Admin and Staff only)"""
    total_count_result = await db.execute(select(func.count(Coupon.id)))
    total_count = total_count_result.scalar()
    
    active_count_result = await db.execute(
        select(func.count(Coupon.id)).where(Coupon.is_active == True)
    )
    active_count = active_count_result.scalar()
    
    return {
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": total_count - active_count,
    }


@router.get("/{coupon_id}", response_model=CouponDetailResponse)
async def get_coupon(
    coupon_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Get a specific coupon (Admin and Staff only)"""
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    return CouponDetailResponse(
        id=coupon.id,
        code=coupon.code,
        discount_percent=coupon.discount_percent,
        is_active=coupon.is_active,
        created_at=coupon.created_at.isoformat(),
    )


@router.post("", response_model=CouponDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Create a new coupon (Admin and Staff only)"""
    result = await db.execute(select(Coupon).where(Coupon.code == coupon_data.code))
    existing_coupon = result.scalar_one_or_none()
    
    if existing_coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    
    new_coupon = Coupon(
        code=coupon_data.code,
        discount_percent=coupon_data.discount_percent,
        is_active=coupon_data.is_active,
    )
    
    db.add(new_coupon)
    await db.commit()
    await db.refresh(new_coupon)
    
    return CouponDetailResponse(
        id=new_coupon.id,
        code=new_coupon.code,
        discount_percent=new_coupon.discount_percent,
        is_active=new_coupon.is_active,
        created_at=new_coupon.created_at.isoformat(),
    )


@router.put("/{coupon_id}", response_model=CouponDetailResponse)
async def update_coupon(
    coupon_id: int,
    coupon_data: CouponUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Update a coupon (Admin and Staff only)"""
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    if coupon_data.code is not None:
        code_check = await db.execute(
            select(Coupon).where(Coupon.code == coupon_data.code, Coupon.id != coupon_id)
        )
        if code_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon code already exists"
            )
        coupon.code = coupon_data.code
    
    if coupon_data.discount_percent is not None:
        coupon.discount_percent = coupon_data.discount_percent
    
    if coupon_data.is_active is not None:
        coupon.is_active = coupon_data.is_active
    
    await db.commit()
    await db.refresh(coupon)
    
    return CouponDetailResponse(
        id=coupon.id,
        code=coupon.code,
        discount_percent=coupon.discount_percent,
        is_active=coupon.is_active,
        created_at=coupon.created_at.isoformat(),
    )


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Delete a coupon (Admin and Staff only)"""
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    await db.delete(coupon)
    await db.commit()
    
    return None
