from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from database.models import User, Coupon
from schemas import UserCreate, UserResponse, Token, LoginRequest, SignUpResponse
from auth import get_password_hash, verify_password, create_access_token
from decimal import Decimal
import random

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate coupon for new user
    names = (user_data.full_name or "").strip().split(maxsplit=1)
    first_name = names[0] if len(names) > 0 else "User"
    last_name = names[1] if len(names) > 1 else ""
    
    first = first_name.replace(" ", "")
    last = last_name.replace(" ", "")
    random_num = random.randint(1000, 9999)
    coupon_code = f"{first}{last}{random_num}"
    
    coupon = Coupon(
        code=coupon_code,
        discount_percent=Decimal(10.0)
    )
    db.add(coupon)
    
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        random_num = random.randint(1000, 9999)
        coupon_code = f"{first}{last}{random_num}"
        coupon.code = coupon_code
        db.add(coupon)
        await db.commit()
    
    await db.refresh(coupon)
    
    # Build response with coupon information
    response_data = SignUpResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        coupon_code=coupon.code,
        coupon_discount=coupon.discount_percent
    )
    
    return response_data


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}
