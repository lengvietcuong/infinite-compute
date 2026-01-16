import pytest
from rag.retrieval.product_search import get_products


@pytest.mark.asyncio
class TestGetProductsTool:
    """Test the get_products tool function"""
    
    async def test_get_products_by_names(self):
        """Test retrieving products by names"""
        result = await get_products(product_names=["4090", "4080"])
        assert "4090" in result or "RTX 4090" in result
        assert "4080" in result or "RTX 4080" in result
        assert "Found" in result
    
    async def test_get_products_with_price_filter(self):
        """Test filtering products by price range"""
        result = await get_products(min_price=500, max_price=1000)
        assert "Found" in result
        assert "$" in result
    
    async def test_get_products_with_memory_filter(self):
        """Test filtering products by minimum memory"""
        result = await get_products(min_memory=16)
        assert "Found" in result
    
    async def test_get_products_by_architecture(self):
        """Test filtering products by architecture"""
        result = await get_products(architecture="Ada Lovelace")
        assert "Found" in result or "No products found" in result
    
    async def test_get_products_by_product_line(self):
        """Test filtering products by product line"""
        result = await get_products(product_line="Consumer Desktop")
        assert "Found" in result or "No products found" in result
    
    async def test_get_products_combined_filters(self):
        """Test using multiple filters together"""
        result = await get_products(
            product_names=["RTX"],
            min_price=500,
            max_price=2000,
            min_memory=12
        )
        assert isinstance(result, str)
        assert "Found" in result or "No products found" in result
    
    async def test_get_products_no_match(self):
        """Test when no products match the criteria"""
        result = await get_products(product_names=["NonExistentProduct12345"])
        assert "No products found" in result
