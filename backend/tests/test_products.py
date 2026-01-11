import pytest
import uuid
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestProducts:
    """Test product endpoints"""
    
    async def test_list_products(self, client: AsyncClient):
        """Test listing all products"""
        response = await client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check product structure
        product = data[0]
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "stock_quantity" in product
        assert "average_rating" in product
        assert "review_count" in product
    
    async def test_list_products_with_search(self, client: AsyncClient):
        """Test product search"""
        response = await client.get("/products?search=RTX")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for product in data:
            assert "RTX" in product["name"] or "RTX" in (product["description"] or "")
    
    async def test_list_products_with_filters(self, client: AsyncClient):
        """Test product filtering"""
        response = await client.get("/products?architecture=Blackwell")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["architecture"] == "Blackwell"
    
    async def test_list_products_price_range(self, client: AsyncClient):
        """Test filtering by price range"""
        response = await client.get("/products?min_price=500&max_price=1000")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            price = float(product["price"])
            assert 500 <= price <= 1000
    
    async def test_list_products_in_stock(self, client: AsyncClient):
        """Test filtering by stock availability"""
        response = await client.get("/products?in_stock=true")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["stock_quantity"] > 0
    
    async def test_get_product_by_id(self, client: AsyncClient, test_product_id: int):
        """Test getting product by ID"""
        response = await client.get(f"/products/{test_product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product_id
        assert "name" in data
        assert "price" in data
    
    async def test_get_nonexistent_product(self, client: AsyncClient):
        """Test getting non-existent product"""
        response = await client.get("/products/999999")
        assert response.status_code == 404
    
    async def test_create_product_as_admin(self, client: AsyncClient, admin_token: str):
        """Test creating product as admin"""
        unique_name = f"Test GPU {uuid.uuid4().hex[:8]}"
        response = await client.post(
            "/products",
            headers=get_auth_headers(admin_token),
            json={
                "name": unique_name,
                "product_line": "Test Line",
                "architecture": "Test Arch",
                "price": 999.99,
                "stock_quantity": 10,
                "description": "Test GPU for API testing"
            }
        )
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == unique_name
        assert float(data["price"]) == 999.99
        pytest.product_counter += 1
    
    async def test_create_product_as_customer(self, client: AsyncClient, customer_token: str):
        """Test creating product as customer (should fail)"""
        response = await client.post(
            "/products",
            headers=get_auth_headers(customer_token),
            json={
                "name": "Unauthorized GPU",
                "price": 999.99,
                "stock_quantity": 10
            }
        )
        assert response.status_code == 403
    
    async def test_create_duplicate_product(self, client: AsyncClient, admin_token: str):
        """Test creating product with duplicate name"""
        # Get existing product name
        response = await client.get("/products?limit=1")
        product_name = response.json()[0]["name"]
        
        response = await client.post(
            "/products",
            headers=get_auth_headers(admin_token),
            json={
                "name": product_name,
                "price": 999.99,
                "stock_quantity": 10
            }
        )
        assert response.status_code == 400
    
    async def test_update_product(self, client: AsyncClient, admin_token: str, test_product_id: int):
        """Test updating product"""
        response = await client.patch(
            f"/products/{test_product_id}",
            headers=get_auth_headers(admin_token),
            json={"stock_quantity": 100}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stock_quantity"] == 100
    
    async def test_delete_product(self, client: AsyncClient, admin_token: str):
        """Test deleting product"""
        # Create a product to delete
        unique_name = f"To Delete {uuid.uuid4().hex[:8]}"
        response = await client.post(
            "/products",
            headers=get_auth_headers(admin_token),
            json={
                "name": unique_name,
                "price": 999.99,
                "stock_quantity": 10
            }
        )
        product_id = response.json()["id"]
        pytest.product_counter += 1
        
        # Delete it
        response = await client.delete(
            f"/products/{product_id}",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(f"/products/{product_id}")
        assert response.status_code == 404


pytest.product_counter = 1
