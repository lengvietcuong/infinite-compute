from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from decimal import Decimal
from database.database import get_db
from database.models import Order, OrderItem, Product, User, OrderStatus
from schemas import OrderCreate, OrderResponse, OrderItemResponse, OrderUpdateStatus, OrderTrackingRequest
from auth import get_current_user, get_current_user_optional, get_current_staff
import secrets

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_tracking_number() -> str:
    """Generate a unique tracking number"""
    return f"INF{secrets.token_hex(6).upper()}"


async def build_order_response(db: AsyncSession, order: Order) -> OrderResponse:
    """Helper function to build OrderResponse with loaded items"""
    result = await db.execute(
        select(OrderItem, Product.name)
        .join(Product, OrderItem.product_id == Product.id, isouter=True)
        .where(OrderItem.order_id == order.id)
    )
    items_with_names = result.all()
    
    items = [
        OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase,
            product_name=name
        )
        for item, name in items_with_names
    ]
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        guest_email=order.guest_email,
        status=order.status,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        tracking_number=order.tracking_number,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create a new order (authenticated users get discount)"""
    # Validate products and calculate total
    total_amount = Decimal(0)
    order_items_data = []
    
    for item in order_data.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
            )
        
        # Apply discount for authenticated users (10%)
        price = product.price
        if current_user:
            price = price * Decimal('0.9')
        
        item_total = price * item.quantity
        total_amount += item_total
        
        order_items_data.append({
            'product': product,
            'quantity': item.quantity,
            'price': price
        })
    
    # Create order
    new_order = Order(
        user_id=current_user.id if current_user else None,
        guest_email=order_data.guest_email if not current_user else None,
        status=OrderStatus.PAID,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        tracking_number=generate_tracking_number()
    )
    
    db.add(new_order)
    await db.flush()
    
    # Create order items and update inventory
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data['product'].id,
            quantity=item_data['quantity'],
            price_at_purchase=item_data['price']
        )
        db.add(order_item)
        
        # Update product stock
        item_data['product'].stock_quantity -= item_data['quantity']
    
    await db.commit()
    await db.refresh(new_order)
    
    return await build_order_response(db, new_order)


@router.get("/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all orders for the authenticated user"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    
    # Build response for each order
    orders_response = []
    for order in orders:
        orders_response.append(await build_order_response(db, order))
    
    return orders_response


@router.post("/track", response_model=List[OrderResponse])
async def track_orders(
    tracking_data: OrderTrackingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Track orders by order ID, email, or tracking number"""
    identifier = tracking_data.identifier.strip()
    
    # Try to find orders by different criteria
    query = select(Order)
    
    # If authenticated, check user's email first
    if current_user:
        query = query.where(
            or_(
                Order.user_id == current_user.id,
                Order.guest_email == identifier,
                Order.tracking_number == identifier
            )
        )
        # Try to parse as order ID
        if identifier.isdigit():
            query = query.where(
                or_(
                    Order.id == int(identifier),
                    Order.user_id == current_user.id,
                    Order.guest_email == identifier,
                    Order.tracking_number == identifier
                )
            )
    else:
        # For guests, only search by email or tracking number
        conditions = [
            Order.guest_email == identifier,
            Order.tracking_number == identifier
        ]
        # Try to parse as order ID
        if identifier.isdigit():
            conditions.append(Order.id == int(identifier))
        
        query = query.where(or_(*conditions))
    
    query = query.order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()
    
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No orders found with the provided information"
        )
    
    # Build response for each order
    orders_response = []
    for order in orders:
        orders_response.append(await build_order_response(db, order))
    
    return orders_response


@router.get("", response_model=List[OrderResponse])
async def list_all_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """List all orders (Staff/Admin only)"""
    query = select(Order)
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Build response for each order
    orders_response = []
    for order in orders:
        orders_response.append(await build_order_response(db, order))
    
    return orders_response


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Update order status (Staff/Admin only)"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = status_data.status
    await db.commit()
    await db.refresh(order)
    
    return await build_order_response(db, order)
