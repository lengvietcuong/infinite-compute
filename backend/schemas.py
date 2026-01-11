from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from database.models import UserRole, OrderStatus, ChatRole


# ==================== User Schemas ====================
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Auth Schemas ====================
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==================== Product Schemas ====================
class ProductBase(BaseModel):
    name: str
    product_line: Optional[str] = None
    architecture: Optional[str] = None
    memory: Optional[str] = None
    memory_type: Optional[str] = None
    cuda_cores: Optional[int] = None
    tensor_cores: Optional[int] = None
    rt_cores: Optional[int] = None
    boost_clock: Optional[str] = None
    tdp: Optional[str] = None
    memory_bandwidth: Optional[str] = None
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    stock_quantity: int = Field(..., ge=0)
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    product_line: Optional[str] = None
    architecture: Optional[str] = None
    memory: Optional[str] = None
    memory_type: Optional[str] = None
    cuda_cores: Optional[int] = None
    tensor_cores: Optional[int] = None
    rt_cores: Optional[int] = None
    boost_clock: Optional[str] = None
    tdp: Optional[str] = None
    memory_bandwidth: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    average_rating: Optional[float] = None
    review_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ==================== News Schemas ====================
class NewsBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    summary: Optional[str] = None
    published_date: Optional[date] = None
    source: Optional[str] = None
    image_url: Optional[str] = None


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    published_date: Optional[date] = None
    source: Optional[str] = None
    image_url: Optional[str] = None


class NewsResponse(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedNewsResponse(BaseModel):
    items: List[NewsResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Order Schemas ====================
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_id: Optional[int]
    quantity: int
    price_at_purchase: Decimal
    product_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    guest_email: Optional[EmailStr] = None
    shipping_address: str
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    user_id: Optional[int]
    guest_email: Optional[str]
    status: OrderStatus
    total_amount: Decimal
    shipping_address: str
    tracking_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


# ==================== Review Schemas ====================
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Chat Schemas ====================
class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    role: ChatRole
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==================== Analytics Schemas ====================
class AnalyticsResponse(BaseModel):
    revenue: Decimal
    total_orders: int
    average_order_value: Decimal
    top_products_units: List[dict]
    top_products_revenue: List[dict]


# ==================== Order Tracking Schema ====================
class OrderTrackingRequest(BaseModel):
    identifier: str  # Can be order ID or email
