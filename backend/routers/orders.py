from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from decimal import Decimal
from database.database import get_db
from database.models import Order, OrderItem, Product, User, OrderStatus, Coupon
from schemas import OrderCreate, OrderResponse, OrderItemResponse, OrderUpdateStatus, OrderUpdate, OrderTrackingRequest, CouponCreate, CouponResponse
from auth import get_current_user, get_current_user_optional, get_current_staff, get_current_admin
import secrets
import random

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_tracking_number() -> str:
    """Generate a unique tracking number in format ORD-xxxxxx where x is A-Z or 0-9"""
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    random_part = "".join(random.choice(characters) for _ in range(6))
    return f"ORD-{random_part}"


async def build_order_response(db: AsyncSession, order: Order, customer_name: Optional[str] = None) -> OrderResponse:
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
        customer_name=customer_name,
        status=order.status,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        tracking_number=order.tracking_number,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items
    )


@router.get("/validate-coupon/{code}", response_model=CouponResponse)
async def validate_coupon(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate a discount coupon"""
    result = await db.execute(
        select(Coupon).where(Coupon.code == code)
    )
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid discount code"
        )
        
    return CouponResponse(code=coupon.code, discount_percent=coupon.discount_percent)


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
        result = await db.execute(
            select(Product).where(Product.id == item.product_id).with_for_update()
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        if product.stock_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{product.name} is out of stock"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
            )
        
        # Determine price (Coupon takes precedence, otherwise Auth user discount)
        price = product.price
        
        # Check discount code
        discount_percent = Decimal(0)
        
        if order_data.discount_code:
            stmt = select(Coupon).where(Coupon.code == order_data.discount_code)
            result = await db.execute(stmt)
            coupon = result.scalar_one_or_none()
            
            if coupon:
                discount_percent = coupon.discount_percent
                # Optional: Mark coupon as used? Or is it reusable? 
                # "10% off coupon". Usually single use. 
                # But implementation details were not strict. 
                # I'll keep it active for simplicity or user re-use.
            # If invalid code, ignore or error? Usually ignore or warn.
        
        if discount_percent > 0:
            # Apply coupon discount
            factor = (Decimal(100) - discount_percent) / Decimal(100)
            price = price * factor
        elif current_user:
            # Apply auth user discount (10%)
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
    
    # Build conditions based on identifier
    conditions = []
    
    # Check if it's a number (could be order ID)
    if identifier.isdigit():
        conditions.append(Order.id == int(identifier))
    
    # Check tracking number (order number in ORD-xxxx format)
    conditions.append(Order.tracking_number == identifier)
    
    # Check guest email
    conditions.append(Order.guest_email == identifier)
    
    # Check if identifier is an email that matches a registered user
    result = await db.execute(select(User).where(User.email == identifier))
    user_by_email = result.scalar_one_or_none()
    if user_by_email:
        conditions.append(Order.user_id == user_by_email.id)
    
    query = select(Order).where(or_(*conditions)).order_by(Order.created_at.desc())
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
    # Join with User to get customer name
    query = select(Order, User.full_name).join(User, Order.user_id == User.id, isouter=True)
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders_with_names = result.all()
    
    # Build response for each order
    orders_response = []
    for order, full_name in orders_with_names:
        # Use full_name if available
        customer_name = full_name
        
        # If not available, try to get from shipping_address (first line)
        if not customer_name:
            if order.shipping_address and '\n' in order.shipping_address:
                customer_name = order.shipping_address.split('\n')[0]
        
        # Fallback to guest email or "Guest"
        if not customer_name:
             customer_name = order.guest_email or "Guest"
             
        orders_response.append(await build_order_response(db, order, customer_name))
    
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


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Update order details (Staff/Admin only)"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    update_data = order_data.model_dump(exclude_unset=True)
    
    if 'user_id' in update_data and update_data['user_id'] is not None:
        user_result = await db.execute(select(User).where(User.id == update_data['user_id']))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {update_data['user_id']} not found"
            )
        order.user_id = update_data['user_id']
        order.guest_email = None
    
    if 'guest_email' in update_data:
        order.guest_email = update_data['guest_email']
        if update_data['guest_email'] is not None:
            order.user_id = None
    
    if 'status' in update_data:
        order.status = update_data['status']
    
    if 'total_amount' in update_data:
        order.total_amount = update_data['total_amount']
    
    if 'shipping_address' in update_data:
        if not update_data['shipping_address'] or not update_data['shipping_address'].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shipping address cannot be empty"
            )
        order.shipping_address = update_data['shipping_address']
    
    if 'tracking_number' in update_data:
        order.tracking_number = update_data['tracking_number']
    
    await db.commit()
    await db.refresh(order)
    
    return await build_order_response(db, order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete an order (Admin only)"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await db.delete(order)
    await db.commit()
    
    return None


@router.post("/coupon/generate", response_model=CouponResponse)
async def generate_coupon(
    coupon_data: CouponCreate,
    db: AsyncSession = Depends(get_db)
):
    """Generate a discount coupon"""
    # Create code format: FirstNameLastNameRandomNum
    # e.g. JohnDoe1234
    first = coupon_data.first_name.replace(" ", "")
    last = coupon_data.last_name.replace(" ", "")
    random_num = random.randint(1000, 9999)
    code = f"{first}{last}{random_num}"
    
    # Check if code already exists (unlikely with random, but good practice)
    # If exists, we could retry, but for now assuming it's unique enough or we return existing?
    # Requirement: "The code should have their first and last name with some random number."
    
    # Create the coupon in DB
    coupon = Coupon(
        code=code,
        discount_percent=Decimal(10.0)
    )
    db.add(coupon)
    try:
        await db.commit()
    except Exception:
        # Fallback if code exists, try one more time? Or just fail?
        # Let's simple retry once
        await db.rollback()
        random_num = random.randint(1000, 9999)
        code = f"{first}{last}{random_num}"
        coupon.code = code
        db.add(coupon)
        await db.commit()

    await db.refresh(coupon)
    return CouponResponse(code=coupon.code, discount_percent=coupon.discount_percent)
