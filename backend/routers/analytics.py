from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal
from database.database import get_db
from database.models import Order, OrderItem, Product, User
from schemas import AnalyticsResponse
from auth import get_current_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    timeframe: Literal["today", "7d", "30d", "90d", "365d", "all"] = Query("30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get analytics data (Admin only)"""
    
    # Calculate date filter based on timeframe
    now = datetime.now(timezone.utc)
    date_filter = None
    
    if timeframe == "today":
        date_filter = now.date()
    elif timeframe == "7d":
        date_filter = now - timedelta(days=7)
    elif timeframe == "30d":
        date_filter = now - timedelta(days=30)
    elif timeframe == "90d":
        date_filter = now - timedelta(days=90)
    elif timeframe == "365d":
        date_filter = now - timedelta(days=365)
    # "all" means no filter
    
    # Build base query
    orders_query = select(Order)
    if date_filter:
        if timeframe == "today":
            orders_query = orders_query.where(func.date(Order.created_at) == date_filter)
        else:
            orders_query = orders_query.where(Order.created_at >= date_filter)
    
    # Get total revenue and order count
    result = await db.execute(
        select(
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).select_from(orders_query.subquery())
    )
    stats = result.first()
    
    revenue = stats.revenue if stats.revenue else Decimal(0)
    total_orders = stats.order_count if stats.order_count else 0
    average_order_value = revenue / total_orders if total_orders > 0 else Decimal(0)
    
    # Get top products by units sold
    order_items_query = select(OrderItem.order_id).select_from(orders_query.subquery())
    
    top_units_result = await db.execute(
        select(
            Product.id,
            Product.name,
            Product.image_url,
            func.sum(OrderItem.quantity).label('units_sold')
        )
        .join(Product, OrderItem.product_id == Product.id)
        .where(OrderItem.order_id.in_(order_items_query))
        .group_by(Product.id, Product.name, Product.image_url)
        .order_by(desc('units_sold'))
        .limit(5)
    )
    top_products_units = [
        {
            'product_id': row.id,
            'product_name': row.name,
            'image_url': row.image_url,
            'units_sold': int(row.units_sold)
        }
        for row in top_units_result
    ]
    
    # Get top products by revenue
    top_revenue_result = await db.execute(
        select(
            Product.id,
            Product.name,
            Product.image_url,
            func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('revenue')
        )
        .join(Product, OrderItem.product_id == Product.id)
        .where(OrderItem.order_id.in_(order_items_query))
        .group_by(Product.id, Product.name, Product.image_url)
        .order_by(desc('revenue'))
        .limit(5)
    )
    top_products_revenue = [
        {
            'product_id': row.id,
            'product_name': row.name,
            'image_url': row.image_url,
            'revenue': float(row.revenue)
        }
        for row in top_revenue_result
    ]

    # Get sales performance over time
    trunc_unit = 'hour' if timeframe == 'today' else 'day'
    date_trunc_col = func.date_trunc(trunc_unit, Order.created_at)
    
    performance_stmt = select(
        date_trunc_col.label('date'),
        func.sum(Order.total_amount).label('revenue'),
        func.count(Order.id).label('orders')
    )
    
    if date_filter:
         if timeframe == "today":
            performance_stmt = performance_stmt.where(func.date(Order.created_at) == date_filter)
         else:
            performance_stmt = performance_stmt.where(Order.created_at >= date_filter)
            
    performance_stmt = performance_stmt.group_by(date_trunc_col).order_by(date_trunc_col)
    
    performance_result = await db.execute(performance_stmt)
    
    sales_performance = [
        {
            'date': row.date,
            'revenue': float(row.revenue) if row.revenue else 0,
            'orders': int(row.orders) if row.orders else 0
        }
        for row in performance_result
    ]
    
    return AnalyticsResponse(
        revenue=revenue,
        total_orders=total_orders,
        average_order_value=average_order_value,
        top_products_units=top_products_units,
        top_products_revenue=top_products_revenue,
        sales_performance=sales_performance
    )
