import asyncio
import csv
import logging
import random
import subprocess
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from pathlib import Path
from typing import Iterable, List

import aiohttp
from faker import Faker
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from config import DATABASE_URL
from database.database import AsyncSessionLocal, Base, engine
from database.models import (
    News,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    Review,
    User,
    UserRole,
)
from rag.add_knowledge import add_markdown_documents, add_markdown_document_chunks


# Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

fake = Faker()

DATA_DIR = Path(__file__).parent.parent / "data"
DATABASE_DIR = Path(__file__).parent
GPUS_CSV = DATA_DIR / "gpus.csv"
NEWS_CSV = DATA_DIR / "news.csv"
DOCUMENTS_DIR = DATA_DIR / "documents"
DATABASE_DUMP_FILE = DATABASE_DIR / "database.dump"


# Database setup
async def restore_database_from_dump() -> bool:
    """Restore database from .dump file using pg_restore."""
    try:
        subprocess.run(
            ["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-acl", "-d", DATABASE_URL, str(DATABASE_DUMP_FILE)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        return True
    except subprocess.TimeoutExpired:
        logger.error("Database restore timed out")
        return False
    except Exception as error:
        logger.error("Error restoring database from dump: %s", error)
        return False


async def create_tables() -> None:
    """Drop and recreate all database tables."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created")


# CSV loaders
async def load_gpus_from_csv(
    session: AsyncSession,
    csv_path: Path,
) -> List[Product]:
    """Load GPU products from a CSV file."""
    if not csv_path.exists():
        logger.error("GPU CSV not found: %s", csv_path)
        return []

    products: List[Product] = []

    with csv_path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            products.append(
                Product(
                    name=row["name"],
                    product_line=row["product_line"],
                    architecture=row["architecture"],
                    memory=row["memory"],
                    memory_type=row["memory_type"],
                    cuda_cores=(
                        int(row["cuda_cores"].replace(",", ""))
                        if row.get("cuda_cores")
                        else None
                    ),
                    tensor_cores=int(row["tensor_cores"])
                    if row.get("tensor_cores")
                    else None,
                    rt_cores=(
                        int(row["rt_cores"])
                        if row.get("rt_cores") not in (None, "N/A")
                        else None
                    ),
                    boost_clock=row["boost_clock"],
                    tdp=row["tdp"],
                    memory_bandwidth=row["memory_bandwidth"],
                    description=row["description"],
                    price=Decimal(row["price_usd"]),
                    stock_quantity=random.randint(5, 50),
                    image_url=row.get("image_url"),
                )
            )

    session.add_all(products)
    await session.commit()

    logger.info("Loaded %d GPU products", len(products))
    return products


async def load_news_from_csv(
    session: AsyncSession,
    csv_path: Path,
) -> List[News]:
    """Load news articles from a CSV file."""
    if not csv_path.exists():
        logger.error("News CSV not found: %s", csv_path)
        return []

    articles: List[News] = []

    with csv_path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            published_date = None
            if row.get("date"):
                try:
                    published_date = datetime.strptime(
                        row["date"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    pass

            articles.append(
                News(
                    title=row["title"],
                    content=row["content"],
                    category=row["category"],
                    summary=row["summary"],
                    published_date=published_date,
                    source=row["source"],
                    image_url=row.get("image_url"),
                )
            )

    session.add_all(articles)
    await session.commit()

    logger.info("Loaded %d news articles", len(articles))
    return articles


# Test data generation
async def create_test_users(session: AsyncSession) -> List[User]:
    """Create fixed and random test users."""
    users: List[User] = [
        User(
            email="customer@gmail.com",
            password_hash=get_password_hash("testing"),
            full_name="Test Customer",
            role=UserRole.CUSTOMER,
        ),
        User(
            email="staff@gmail.com",
            password_hash=get_password_hash("testing"),
            full_name="Test Staff",
            role=UserRole.STAFF,
        ),
        User(
            email="admin@gmail.com",
            password_hash=get_password_hash("testing"),
            full_name="Test Admin",
            role=UserRole.ADMIN,
        ),
    ]

    for _ in range(random.randint(20, 30)):
        users.append(
            User(
                email=fake.unique.email(),
                password_hash=get_password_hash("test123"),
                full_name=fake.name(),
                role=UserRole.CUSTOMER,
            )
        )

    session.add_all(users)
    await session.commit()

    for user in users:
        await session.refresh(user)

    logger.info("Created %d users", len(users))
    return users


async def create_orders(
    session: AsyncSession,
    users: Iterable[User],
    products: List[Product],
) -> List[Order]:
    """Create realistic orders using an 80/20 revenue distribution."""
    customers = [u for u in users if u.role == UserRole.CUSTOMER]
    if not customers or not products:
        return []

    orders: List[Order] = []
    order_items: List[OrderItem] = []

    products_sorted = sorted(products, key=lambda p: p.price, reverse=True)
    top_products = products_sorted[: max(1, len(products) // 5)]
    other_products = products_sorted[len(top_products) :]

    for _ in range(random.randint(50, 100)):
        days_ago = random.randint(0, 30)
        created_at = datetime.now(UTC) - timedelta(days=days_ago)

        is_guest = random.random() < 0.3
        user = None if is_guest else random.choice(customers)

        selected_items = []
        for _ in range(random.randint(1, 4)):
            pool = top_products if random.random() < 0.8 else other_products
            if not pool:
                pool = products
            product = random.choice(pool)
            selected_items.append((product, random.randint(1, 3)))

        total = Decimal(0)
        for product, qty in selected_items:
            price = product.price * (Decimal("0.9") if user else Decimal(1))
            total += price * qty

        status = (
            OrderStatus.DELIVERED
            if days_ago > 14
            else random.choice(
                [OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
            )
        )

        order = Order(
            user_id=user.id if user else None,
            guest_email=None if user else fake.email(),
            status=status,
            total_amount=total,
            shipping_address=f"{user.full_name if user else fake.name()}\n{fake.address()}",
            tracking_number=f"ORD-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))}",
            created_at=created_at,
            updated_at=created_at,
        )

        session.add(order)
        await session.flush()

        for product, qty in selected_items:
            order_items.append(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    price_at_purchase=product.price,
                )
            )

        orders.append(order)

    session.add_all(order_items)
    await session.commit()

    logger.info("Created %d orders", len(orders))
    return orders


async def create_reviews(session: AsyncSession) -> List[Review]:
    """Create reviews for shipped or delivered orders."""
    result = await session.execute(
        select(Order).where(
            Order.status.in_([OrderStatus.SHIPPED, OrderStatus.DELIVERED])
        )
    )
    orders = result.scalars().all()
    if not orders:
        return []

    reviews: List[Review] = []
    reviewed = set()

    REVIEW_TEMPLATES = {
        5: [
            "Excellent GPU! Runs all my games at max settings. Highly recommend!",
            "Outstanding performance! This card exceeded my expectations. Worth every penny.",
            "Perfect for my needs. Fast shipping and great quality. Five stars!",
            "Best GPU I've ever owned. Handles everything I throw at it with ease.",
            "Amazing performance for the price. Very satisfied with this purchase!",
            "Flawless performance! Great for gaming and rendering. Couldn't be happier.",
            "This GPU is a beast! Runs cool and quiet even under heavy load.",
            "Incredible value! Performance is top-notch for both gaming and productivity.",
            "Absolutely love this card! Handles 4K gaming like a champ.",
            "Zero regrets with this purchase. The performance is phenomenal!",
            "Best investment for my gaming setup. Runs everything maxed out effortlessly.",
            "Superb build quality and amazing temps. Couldn't ask for more!",
            "This GPU crushes every benchmark! Very impressed with the performance.",
            "Premium quality at a reasonable price. Delivery was quick too!",
            "Spectacular card! My renders finish in half the time now.",
            "Top tier performance! Worth saving up for. Highly satisfied!",
        ],
        4: [
            "Great GPU overall. Minor coil whine but performance is solid.",
            "Good performance for the price. Runs a bit hot but manageable.",
            "Very satisfied! Only giving 4 stars because shipping took longer than expected.",
            "Solid card. Does what it says on the tin. Would recommend.",
            "Good value for money. Performance is great, though drivers could be better.",
            "Happy with my purchase. Runs most games smoothly with high settings.",
            "Quality product. Lost one star due to the high power consumption.",
            "Really good GPU! Minor issue with fan noise but nothing major.",
            "Performance is excellent. Only concern is the size - barely fits in my case.",
            "Strong performer! Would be 5 stars if the RGB software was better.",
            "Very pleased overall. Installation was smooth and performance is solid.",
            "Great for 1440p gaming. Occasionally hits thermal limits under stress.",
            "Good card but could use better cooling. Still happy with the purchase.",
            "Performs well in all tasks. Packaging could be better but the product is fine.",
        ],
        3: [
            "Decent GPU but nothing special. Gets the job done.",
            "Average performance. Works fine but expected more for the price.",
            "It's okay. Performance is acceptable but not outstanding.",
            "Does what it needs to do. Not blown away but not disappointed either.",
            "Middle of the road. Good for casual gaming but struggles with demanding titles.",
            "Fair product. Some driver issues but overall functional.",
            "Adequate for my needs. Nothing exceptional but it works.",
            "Meets basic expectations. Performance is average for this price point.",
            "It's fine. Does the job but I've seen better for similar money.",
            "Standard performance. No major issues but nothing to write home about.",
        ],
        2: [
            "Disappointed with the performance. Runs hotter than expected.",
            "Not worth the price. Had several crashes and stability issues.",
            "Below expectations. Thermal throttling is a real problem.",
            "Having driver issues constantly. Customer support wasn't helpful.",
            "Underperforms compared to specifications. Would not buy again.",
            "Too many problems for the price. Frequent crashes during gaming.",
            "Not satisfied. The card runs way too hot and loud under load.",
            "Expected better. Performance doesn't match what was advertised.",
            "Regret this purchase. Too many compatibility issues with my setup.",
        ],
        1: [
            "Terrible experience. Card died after two weeks. Avoid!",
            "Complete waste of money. Constant crashes and artifacts.",
            "DOA - Dead on arrival. Had to return immediately.",
            "Worst purchase ever. Nothing but problems from day one.",
            "Save your money. This GPU is unreliable and underperforms badly.",
            "Absolute disaster. Artifacting within hours of use. Returning ASAP.",
            "Don't waste your time. This card is defective and support is useless.",
            "Horrible quality control. Mine was broken right out of the box.",
        ],
    }

    for order in random.sample(orders, int(len(orders) * 0.95)):
        if not order.user_id:
            continue

        items = (
            await session.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
        ).scalars()

        for item in items:
            key = (order.user_id, item.product_id)
            if key in reviewed or random.random() > 0.95:
                continue

            rating = random.choices(
                [1, 2, 3, 4, 5], weights=[2, 3, 10, 35, 50]
            )[0]

            comment = random.choice(REVIEW_TEMPLATES[rating])

            reviews.append(
                Review(
                    user_id=order.user_id,
                    product_id=item.product_id,
                    rating=rating,
                    comment=comment,
                    created_at=order.created_at + timedelta(days=random.randint(1, 7)),
                )
            )
            reviewed.add(key)

    session.add_all(reviews)
    await session.commit()

    logger.info("Created %d reviews", len(reviews))
    return reviews


# Initialization entry point
async def initialize_database() -> None:
    logger.info("Starting database initialization")

    if DATABASE_DUMP_FILE.exists():
        logger.info("Loading database from .dump file...")
        dump_restored = await restore_database_from_dump()
        if dump_restored:
            logger.info("Database initialization complete")
            return

    await create_tables()
    async with AsyncSessionLocal() as session:
        products = await load_gpus_from_csv(session, GPUS_CSV)
        await load_news_from_csv(session, NEWS_CSV)
        users = await create_test_users(session)
        await create_orders(session, users, products)
        await create_reviews(session)

    logger.info("Adding Markdown documents")
    await add_markdown_documents(DOCUMENTS_DIR)

    logger.info("Adding Markdown document chunks")
    async with aiohttp.ClientSession() as http_session:
        await add_markdown_document_chunks(
            DOCUMENTS_DIR,
            http_session,
            asyncio.Semaphore(5),
        )

    logger.info("Database initialization complete")


if __name__ == "__main__":
    asyncio.run(initialize_database())
