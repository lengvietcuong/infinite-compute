"""Module for searching GPU products in the database and retrieving their information."""

from sqlalchemy import select, func

from database.database import AsyncSessionLocal
from database.models import Product, Review


async def list_products() -> str:
    """
    List all product names available in the database.

    Returns:
        str: Formatted list of all product names
    """
    async with AsyncSessionLocal() as db:
        query = select(Product.name).order_by(Product.name)
        result = await db.execute(query)
        product_names = result.scalars().all()

        if not product_names:
            return "No products found in the database."

        product_list = "\n".join(f"- {name}" for name in product_names)
        return f"Available products ({len(product_names)} total):\n{product_list}"


async def get_product(product_name: str) -> str:
    """
    Search for a GPU product by name and retrieve all its information.

    Args:
        product_name (str): The product name or partial name to search for

    Returns:
        str: Formatted product information
    """
    async with AsyncSessionLocal() as db:
        # First, try exact match (case-insensitive)
        exact_query = select(Product).where(func.lower(Product.name) == func.lower(product_name))
        exact_result = await db.execute(exact_query)
        exact_product = exact_result.scalar_one_or_none()
        
        if exact_product:
            products = [exact_product]
        else:
            # Fall back to partial match
            search_pattern = f"%{product_name}%"
            query = select(Product).where(Product.name.ilike(search_pattern))
            result = await db.execute(query)
            products = result.scalars().all()

        if not products:
            raise ValueError(f"No product found matching '{product_name}'.")

        if len(products) > 1:
            product_names = [p.name for p in products]
            raise ValueError(f"Multiple products found matching '{product_name}':\n" + "\n".join(f"- {name}" for name in product_names) + "\n\nPlease be more specific.")

        product = products[0]

        review_stats = await db.execute(
            select(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            ).where(Review.product_id == product.id)
        )
        stats = review_stats.first()
        average_rating = float(stats.avg_rating) if stats.avg_rating else None
        review_count = stats.review_count

        product_info = [
            f"Product: {product.name}",
            f"ID: {product.id}",
            f"Price: ${product.price}",
            f"Stock: {product.stock_quantity} units",
        ]

        if product.product_line:
            product_info.append(f"Product Line: {product.product_line}")
        if product.architecture:
            product_info.append(f"Architecture: {product.architecture}")
        if product.memory:
            product_info.append(f"Memory: {product.memory}")
        if product.memory_type:
            product_info.append(f"Memory Type: {product.memory_type}")
        if product.cuda_cores:
            product_info.append(f"CUDA Cores: {product.cuda_cores}")
        if product.tensor_cores:
            product_info.append(f"Tensor Cores: {product.tensor_cores}")
        if product.rt_cores:
            product_info.append(f"RT Cores: {product.rt_cores}")
        if product.boost_clock:
            product_info.append(f"Boost Clock: {product.boost_clock}")
        if product.tdp:
            product_info.append(f"TDP: {product.tdp}")
        if product.memory_bandwidth:
            product_info.append(f"Memory Bandwidth: {product.memory_bandwidth}")
        if product.description:
            product_info.append(f"Description: {product.description}")

        if average_rating is not None:
            product_info.append(f"Average Rating: {average_rating:.1f}/5.0 ({review_count} reviews)")
        else:
            product_info.append("No reviews yet")

        if product.image_url:
            product_info.append(f"Image URL: {product.image_url}")

        return "\n".join(product_info)