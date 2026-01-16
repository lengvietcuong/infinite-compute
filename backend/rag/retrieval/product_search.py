"""Module for searching GPU products in the database and retrieving their information."""

from typing import Optional, List
from sqlalchemy import select, func, and_, Integer, or_

from database.database import AsyncSessionLocal
from database.models import Product, Review


async def get_products(
    product_names: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_memory: Optional[int] = None,
    product_line: Optional[str] = None,
    architecture: Optional[str] = None,
    min_stock: Optional[int] = None,
) -> str:
    """
    Search for GPU products with optional filters.

    Args:
        product_names (Optional[List[str]]): List of product names to retrieve. Uses partial matching (e.g., ["4090", "4080"] will match "GeForce RTX 4090" and "GeForce RTX 4080")
        min_price (Optional[float]): Minimum price filter
        max_price (Optional[float]): Maximum price filter
        min_memory (Optional[int]): Minimum memory in GB (e.g., 8, 12, 16, 24)
        product_line (Optional[str]): Filter by product line. Available values: 'Consumer Desktop', 'Consumer Laptop', 'Data Center', 'Professional Desktop'
        architecture (Optional[str]): Filter by architecture. Available values: 'Blackwell', 'Ada', 'Hopper', 'Ampere', 'Turing'
        min_stock (Optional[int]): Minimum stock quantity (default: 1 to show only in-stock items)

    Returns:
        str: Formatted list of products matching the criteria
    """
    async with AsyncSessionLocal() as db:
        # Build the query with filters
        conditions = []
        
        if product_names is not None and len(product_names) > 0:
            # Create OR conditions for each product name (case-insensitive partial match)
            name_conditions = []
            for name in product_names:
                name_conditions.append(Product.name.ilike(f"%{name}%"))
            conditions.append(or_(*name_conditions))
        
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)
        if min_memory is not None:
            # Use REGEXP_REPLACE to extract the first numeric value from memory string
            # Handles formats like "24GB", "32 GB", "16GB/8GB"
            memory_value = func.cast(
                func.regexp_replace(Product.memory, r'[^0-9].*$', ''),
                Integer
            )
            conditions.append(memory_value >= min_memory)
        if product_line is not None:
            conditions.append(Product.product_line.ilike(f"%{product_line}%"))
        if architecture is not None:
            conditions.append(Product.architecture.ilike(f"%{architecture}%"))
        if min_stock is not None:
            conditions.append(Product.stock_quantity >= min_stock)
        else:
            # By default, only show products in stock
            conditions.append(Product.stock_quantity > 0)
        
        query = select(Product).order_by(Product.price.asc())
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        products = result.scalars().all()

        if not products:
            return "No products found matching the specified criteria."

        # Format the product list
        product_lines = []
        for product in products:
            specs = []
            if product.memory:
                specs.append(product.memory)
            if product.memory_type:
                specs.append(product.memory_type)
            if product.cuda_cores:
                specs.append(f"{product.cuda_cores} CUDA cores")
            
            specs_str = ", ".join(specs) if specs else "No specs available"
            stock_status = f"{product.stock_quantity} in stock" if product.stock_quantity > 0 else "Out of stock"
            
            product_lines.append(
                f"- {product.name} (${product.price})\n"
                f"  Specs: {specs_str}\n"
                f"  Stock: {stock_status}"
            )
        
        filter_summary = []
        if product_names is not None and len(product_names) > 0:
            filter_summary.append(f"names matching {product_names}")
        if min_price is not None:
            filter_summary.append(f"min price ${min_price}")
        if max_price is not None:
            filter_summary.append(f"max price ${max_price}")
        if min_memory is not None:
            filter_summary.append(f"min {min_memory}GB memory")
        if product_line is not None:
            filter_summary.append(f"product line '{product_line}'")
        if architecture is not None:
            filter_summary.append(f"architecture '{architecture}'")
        
        filter_text = f" (Filters: {', '.join(filter_summary)})" if filter_summary else ""
        
        return (
            f"Found {len(products)} product(s){filter_text}:\n\n"
            + "\n\n".join(product_lines)
        )


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

        return "\n".join(product_info)