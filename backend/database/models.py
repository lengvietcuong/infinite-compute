import enum
import uuid

from database.database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    Date,
    DECIMAL,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config import EMBEDDING_DIMENSIONS


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"


class OrderStatus(str, enum.Enum):
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    orders = relationship("Order", back_populates="user")
    reviews = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    product_line = Column(String(100))
    architecture = Column(String(100))
    memory = Column(String(50))
    memory_type = Column(String(50))
    cuda_cores = Column(Integer)
    tensor_cores = Column(Integer)
    rt_cores = Column(Integer)
    boost_clock = Column(String(50))
    tdp = Column(String(50))
    memory_bandwidth = Column(String(50))
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    stock_quantity = Column(Integer, nullable=False, default=0)
    image_url = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan"
    )


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    summary = Column(Text)
    published_date = Column(Date, index=True)
    source = Column(String(255))
    image_url = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_percent = Column(DECIMAL(5, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    guest_email = Column(String(255), index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PAID, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    shipping_address = Column(Text, nullable=False)
    tracking_number = Column(String(100))
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(DECIMAL(10, 2), nullable=False)

    __table_args__ = (CheckConstraint("quantity > 0", name="check_quantity_positive"),)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class ChatSession(Base):
    __tablename__ = "chat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("chat.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(SQLEnum(ChatRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class DocumentChunk(Base):
    """SQLAlchemy model for document chunks with embeddings."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    content = Column(
        Text,
        CheckConstraint("length(content) > 0"),
        nullable=False,
    )
    embedding = Column(Vector(EMBEDDING_DIMENSIONS), nullable=False)
    source_file = Column(
        String(255),
        CheckConstraint("length(source_file) > 0"),
        nullable=False,
    )
    chunk_index = Column(Integer, nullable=False)
    sha256_hash = Column(
        LargeBinary(32),
        Computed("digest(content, 'sha256')", persisted=True),
        nullable=False,
        unique=True,
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index(
            "idx_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class Document(Base):
    """SQLAlchemy model for full documents."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    content = Column(
        Text,
        CheckConstraint("length(content) > 0"),
        nullable=False,
    )
    topic = Column(
        Text,
        CheckConstraint("length(topic) > 0"),
        nullable=False,
    )
    source_file = Column(
        String(255),
        CheckConstraint("length(source_file) > 0"),
        nullable=False,
        unique=True,
        index=True,
    )
    sha256_hash = Column(
        LargeBinary(32),
        Computed("digest(content, 'sha256')", persisted=True),
        nullable=False,
        unique=True,
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )
