import asyncio
import csv
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import engine, Base, AsyncSessionLocal
from database.models import Product, News

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
                price=float(row['price_usd']),
                stock_quantity=10,
                image_url=None
            )
            products.append(product)
    
    session.add_all(products)
    await session.commit()
    logger.info(f"Loaded {len(products)} GPU products from CSV")


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
                image_url=None,  # Will be set manually or through admin interface
                author_id=None  # Will be set when staff/admin posts
            )
            news_articles.append(article)
    
    session.add_all(news_articles)
    await session.commit()
    logger.info(f"Loaded {len(news_articles)} news articles from CSV")


async def initialize_database():
    """Main function to initialize the database"""
    logger.info("Starting database initialization...")
    
    # Define CSV file paths
    data_dir = Path(__file__).parent.parent / "data"
    gpus_csv_path = data_dir / "nvidia_gpus.csv"
    news_csv_path = data_dir / "news.csv"
    
    # Create tables
    await create_tables()
    
    # Load data from CSV files
    async with AsyncSessionLocal() as session:
        await load_gpus_from_csv(session, gpus_csv_path)
        await load_news_from_csv(session, news_csv_path)
    
    logger.info("Database initialization completed successfully!")


if __name__ == "__main__":
    asyncio.run(initialize_database())
