import asyncio
import csv
import logging
import random
from pathlib import Path
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import engine, Base, AsyncSessionLocal
from database.models import (
    Product, News, User, UserRole, Order, OrderItem, OrderStatus, 
    Review, ChatSession, ChatMessage, ChatRole
)
from auth import get_password_hash
from faker import Faker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

fake = Faker()


async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def load_gpus_from_csv(session: AsyncSession, csv_path: Path):
    """Load GPU data from CSV file into products table"""
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    products = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            product = Product(
                name=row['name'],
                product_line=row['product_line'],
                architecture=row['architecture'],
                memory=row['memory'],
                memory_type=row['memory_type'],
                cuda_cores=int(row['cuda_cores'].replace(',', '')) if row['cuda_cores'] else None,
                tensor_cores=int(row['tensor_cores']) if row['tensor_cores'] else None,
                rt_cores=int(row['rt_cores']) if row['rt_cores'] and row['rt_cores'] != 'N/A' else None,
                boost_clock=row['boost_clock'],
                tdp=row['tdp'],
                memory_bandwidth=row['memory_bandwidth'],
                description=row['description'],
                price=Decimal(row['price_usd']),
                stock_quantity=random.randint(5, 50),  # Random stock between 5-50
                image_url=row.get('image_url')
            )
            products.append(product)
    
    session.add_all(products)
    await session.commit()
    logger.info(f"Loaded {len(products)} GPU products from CSV")
    return products


async def load_news_from_csv(session: AsyncSession, csv_path: Path):
    """Load news data from CSV file into news table"""
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    news_articles = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            published_date = None
            if row['date']:
                try:
                    published_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            article = News(
                title=row['title'],
                content=row['content'],
                category=row['category'],
                summary=row['summary'],
                published_date=published_date,
                source=row['source'],
                image_url=row.get('image_url')
            )
            news_articles.append(article)
    
    session.add_all(news_articles)
    await session.commit()
    logger.info(f"Loaded {len(news_articles)} news articles from CSV")
    return news_articles


async def create_test_users(session: AsyncSession):
    """Create test users with different roles"""
    users = [
        User(
            email="customer@gmail.com",
            password_hash=get_password_hash("testing"),
            full_name="Test Customer",
            role=UserRole.CUSTOMER
        ),
        User(
            email="staff@gmail.com",
            password_hash=get_password_hash("testing"),
            full_name="Test Staff",
            role=UserRole.STAFF
        ),
        User(
            email="admin@gmail.com",
            password_hash=get_password_hash("testing"),
            full_name="Test Admin",
            role=UserRole.ADMIN
        )
    ]
    
    # Create additional random customers (20-30)
    num_customers = random.randint(20, 30)
    for i in range(num_customers):
        users.append(User(
            email=fake.unique.email(),
            password_hash=get_password_hash("test123"),
            full_name=fake.name(),
            role=UserRole.CUSTOMER
        ))
    
    session.add_all(users)
    await session.commit()
    
    # Refresh to get IDs
    for user in users:
        await session.refresh(user)
    
    logger.info(f"Created {len(users)} users")
    return users


async def create_orders(session: AsyncSession, users, products):
    """Create realistic order history following the Pareto principle (80/20 rule)"""
    orders = []
    order_items = []
    
    # Get customer users only
    customers = [u for u in users if u.role == UserRole.CUSTOMER]
    
    # Implement Pareto principle: top 20% of products generate 80% of revenue
    num_products = len(products)
    num_top_products = max(1, num_products // 5)
    
    top_products = products[:num_top_products]
    remaining_products = products[num_top_products:]
    
    # Create 50-100 orders spread over the last 6 months
    num_orders = random.randint(50, 100)
    
    for _ in range(num_orders):
        # Random date in the last 180 days
        days_ago = random.randint(0, 180)
        order_date = datetime.now(UTC) - timedelta(days=days_ago)
        
        # 70% authenticated, 30% guest
        is_guest = random.random() < 0.3
        
        if is_guest:
            user_id = None
            guest_email = fake.email()
            guest_name = fake.name()
        else:
            user = random.choice(customers)
            user_id = user.id
            guest_email = None
            guest_name = user.full_name
        
        # Select products with heavy bias towards top 20%
        num_items = random.randint(1, 3)
        selected_products = []
        
        for _ in range(num_items):
            # 95% chance to select from top 20% products, 5% from remaining 80%
            if random.random() < 0.95 and top_products:
                product = random.choice(top_products)
                # Top products have higher quantities (1-3 units)
                quantity = random.randint(1, 3)
            elif remaining_products:
                product = random.choice(remaining_products)
                # Remaining products have lower quantities (1-2 units)
                quantity = random.randint(1, 2)
            else:
                product = random.choice(products)
                quantity = random.randint(1, 2)
            
            selected_products.append((product, quantity))
        
        # Calculate total (with discount for authenticated users)
        total_amount = Decimal(0)
        items_for_order = []
        
        for product, quantity in selected_products:
            price = product.price
            
            # Apply 10% discount for authenticated users
            if not is_guest:
                price = price * Decimal('0.9')
            
            total_amount += price * quantity
            items_for_order.append({
                'product_id': product.id,
                'quantity': quantity,
                'price': price
            })
        
        # Determine order status based on age
        if days_ago > 30:
            status = random.choices(
                [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
                weights=[0.95, 0.05]
            )[0]
        elif days_ago > 7:
            status = random.choices(
                [OrderStatus.DELIVERED, OrderStatus.SHIPPED, OrderStatus.CANCELLED],
                weights=[0.85, 0.13, 0.02]
            )[0]
        else:
            status = random.choices(
                [OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED],
                weights=[0.4, 0.5, 0.1]
            )[0]
        
        # Generate tracking number in format ORD-xxxxxx (6 random alphanumeric characters)
        random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        
        # Format shipping address with customer name on first line (matching checkout page format)
        address_parts = fake.address().split('\n')
        shipping_address = f"{guest_name}\n{', '.join(address_parts)}"
        
        order = Order(
            user_id=user_id,
            guest_email=guest_email,
            status=status,
            total_amount=total_amount,
            shipping_address=shipping_address,
            tracking_number=f"ORD-{random_chars}",
            created_at=order_date,
            updated_at=order_date
        )
        
        session.add(order)
        await session.flush()
        
        # Create order items
        for item_data in items_for_order:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price_at_purchase=item_data['price']
            )
            order_items.append(order_item)
        
        orders.append(order)
    
    session.add_all(order_items)
    await session.commit()
    
    # Calculate actual revenue distribution for verification
    product_revenue = {}
    for order_item in order_items:
        product_id = order_item.product_id
        revenue = order_item.price_at_purchase * order_item.quantity
        product_revenue[product_id] = product_revenue.get(product_id, Decimal(0)) + revenue
    
    total_revenue = sum(product_revenue.values())
    top_product_ids = {p.id for p in top_products}
    top_revenue = sum(rev for pid, rev in product_revenue.items() if pid in top_product_ids)
    
    top_revenue_percentage = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    logger.info(f"Created {len(orders)} orders with {len(order_items)} order items")
    logger.info(f"Top 20% products ({num_top_products} products) generated {top_revenue_percentage:.1f}% of revenue")
    logger.info(f"Remaining 80% products ({len(remaining_products)} products) generated {100 - top_revenue_percentage:.1f}% of revenue")
    return orders


async def create_reviews(session: AsyncSession, users, products, orders):
    """Create reviews for shipped/delivered orders"""
    reviews = []
    customers = [u for u in users if u.role == UserRole.CUSTOMER]
    
    # Get all shipped/delivered orders
    result = await session.execute(
        select(Order).where(Order.status.in_([OrderStatus.SHIPPED, OrderStatus.DELIVERED]))
    )
    eligible_orders = result.scalars().all()
    
    # 60% of eligible orders get reviews
    orders_to_review = random.sample(
        eligible_orders, 
        int(len(eligible_orders) * 0.6)
    )
    
    reviewed_combinations = set()
    
    for order in orders_to_review:
        if not order.user_id:
            continue
        
        # Get order items
        result = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = result.scalars().all()
        
        for item in items:
            if not item.product_id:
                continue
            
            # Check if user already reviewed this product
            combo = (order.user_id, item.product_id)
            if combo in reviewed_combinations:
                continue
            
            # 70% chance to review each product
            if random.random() < 0.7:
                # Weighted ratings (more likely to be positive)
                rating = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[0.02, 0.03, 0.10, 0.35, 0.50]
                )[0]
                
                # 80% chance to include a comment
                comment = None
                if random.random() < 0.8:
                    if rating >= 4:
                        comment = random.choice([
                            "Excellent GPU! Highly recommend.",
                            "Works perfectly for my needs. Great performance!",
                            "Amazing card, runs all my games flawlessly.",
                            "Very satisfied with this purchase. Fast shipping too!",
                            "Best GPU I've owned. Worth every penny.",
                            "Incredible performance for AI workloads!",
                            "Ray tracing looks amazing. No regrets!",
                            "Perfect for 4K gaming. Very happy!",
                            "Silent and powerful. Great build quality.",
                            "Exceeded my expectations. Highly recommended!"
                        ])
                    elif rating == 3:
                        comment = random.choice([
                            "Good GPU but a bit pricey.",
                            "Does the job, nothing special.",
                            "Decent performance, expected more.",
                            "It's okay for the price.",
                            "Works as advertised."
                        ])
                    else:
                        comment = random.choice([
                            "Had some issues with temperatures.",
                            "Not as fast as I hoped.",
                            "Disappointed with the performance.",
                            "Overpriced for what it offers.",
                            "Had driver issues initially."
                        ])
                
                # Review date is 1-30 days after order
                review_date = order.created_at + timedelta(days=random.randint(1, 30))
                
                review = Review(
                    user_id=order.user_id,
                    product_id=item.product_id,
                    rating=rating,
                    comment=comment,
                    created_at=review_date,
                    updated_at=review_date
                )
                reviews.append(review)
                reviewed_combinations.add(combo)
    
    session.add_all(reviews)
    await session.commit()
    
    logger.info(f"Created {len(reviews)} reviews")
    return reviews


async def create_chat_sessions(session: AsyncSession, users):
    """Create chat sessions and messages for customers"""
    chat_sessions = []
    chat_messages = []
    
    customers = [u for u in users if u.role == UserRole.CUSTOMER]
    
    # 40% of customers have chat history
    customers_with_chats = random.sample(
        customers,
        int(len(customers) * 0.4)
    )
    
    for customer in customers_with_chats:
        # 1-3 chat sessions per customer
        num_sessions = random.randint(1, 3)
        
        for _ in range(num_sessions):
            session_date = datetime.now(UTC) - timedelta(days=random.randint(0, 180))
            
            chat_session = ChatSession(
                user_id=customer.id,
                title=random.choice([
                    "GPU Recommendation",
                    "Technical Support",
                    "Product Comparison",
                    "Purchase Inquiry",
                    "Performance Questions",
                    "Compatibility Check",
                    "Upgrade Advice"
                ]),
                created_at=session_date,
                updated_at=session_date
            )
            
            session.add(chat_session)
            await session.flush()
            
            # 2-8 messages per session
            num_messages = random.randint(2, 8)
            
            for i in range(num_messages):
                role = ChatRole.USER if i % 2 == 0 else ChatRole.ASSISTANT
                
                if role == ChatRole.USER:
                    content = random.choice([
                        "What GPU would you recommend for 4K gaming?",
                        "Can this card handle AI workloads?",
                        "What's the difference between these two models?",
                        "Is this GPU good for video editing?",
                        "Do I need to upgrade my power supply?",
                        "Will this fit in my case?",
                        "What's the best value GPU right now?",
                        "Can I run DLSS on this card?"
                    ])
                else:
                    content = random.choice([
                        "Based on your requirements, I'd recommend the RTX 5080 for excellent 4K performance.",
                        "Yes, this GPU has excellent tensor cores for AI workloads.",
                        "The main difference is in CUDA core count and memory bandwidth.",
                        "This card is excellent for video editing with hardware encoding.",
                        "For this GPU, a 750W power supply is recommended.",
                        "This is a dual-slot card, it should fit in most standard cases.",
                        "The RTX 5070 offers the best price-to-performance ratio currently.",
                        "Yes, all RTX 50 series cards support DLSS 4 with frame generation."
                    ])
                
                message_date = session_date + timedelta(minutes=i * 2)
                
                chat_message = ChatMessage(
                    session_id=chat_session.id,
                    role=role,
                    content=content,
                    created_at=message_date
                )
                chat_messages.append(chat_message)
            
            chat_sessions.append(chat_session)
    
    session.add_all(chat_messages)
    await session.commit()
    
    logger.info(f"Created {len(chat_sessions)} chat sessions with {len(chat_messages)} messages")
    return chat_sessions


async def initialize_database():
    """Main function to initialize the database"""
    logger.info("Starting database initialization...")
    
    # Define CSV file paths
    data_dir = Path(__file__).parent.parent / "data"
    gpus_csv_path = data_dir / "gpus.csv"
    news_csv_path = data_dir / "news.csv"
    
    # Create tables
    await create_tables()
    
    # Load data from CSV files and create comprehensive test data
    async with AsyncSessionLocal() as session:
        products = await load_gpus_from_csv(session, gpus_csv_path)
        news = await load_news_from_csv(session, news_csv_path)
        users = await create_test_users(session)
        orders = await create_orders(session, users, products)
        reviews = await create_reviews(session, users, products, orders)
        chat_sessions = await create_chat_sessions(session, users)
    
    logger.info("Database initialization completed successfully!")
    logger.info("\n" + "="*60)
    logger.info("TEST ACCOUNTS:")
    logger.info("  Customer: customer@gmail.com / testing")
    logger.info("  Staff:    staff@gmail.com / testing")
    logger.info("  Admin:    admin@gmail.com / testing")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(initialize_database())
