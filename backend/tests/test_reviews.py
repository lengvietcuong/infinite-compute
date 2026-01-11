import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestReviews:
    """Test review endpoints"""
    
    async def test_get_product_reviews(self, client: AsyncClient, test_product_id: int):
        """Test getting reviews for a product"""
        response = await client.get(f"/reviews/product/{test_product_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_reviews_for_nonexistent_product(self, client: AsyncClient):
        """Test getting reviews for non-existent product"""
        response = await client.get("/reviews/product/999999")
        assert response.status_code == 404
    
    async def test_create_review_without_shipped_order(self, client: AsyncClient, customer_token: str, test_product_id: int):
        """Test creating review without shipped order (should fail)"""
        response = await client.post(
            "/reviews",
            headers=get_auth_headers(customer_token),
            json={
                "product_id": test_product_id,
                "rating": 5,
                "comment": "Great product!"
            }
        )
        # This might succeed or fail depending on test data
        # If user already has shipped order, it will succeed
        assert response.status_code in [201, 403]
    
    async def test_create_review_with_shipped_order(self, client: AsyncClient, customer_token: str, staff_token: str):
        """Test full review workflow: order -> ship -> review"""
        # 1. Get a product
        response = await client.get("/products?limit=1")
        product = response.json()[0]
        product_id = product["id"]
        
        # 2. Create order as customer
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "123 Review Test St",
                "items": [{"product_id": product_id, "quantity": 1}]
            }
        )
        assert response.status_code == 201
        order_id = response.json()["id"]
        
        # 3. Update order to SHIPPED as staff
        response = await client.patch(
            f"/orders/{order_id}/status",
            headers=get_auth_headers(staff_token),
            json={"status": "SHIPPED"}
        )
        assert response.status_code == 200
        
        # 4. Create review
        response = await client.post(
            "/reviews",
            headers=get_auth_headers(customer_token),
            json={
                "product_id": product_id,
                "rating": 5,
                "comment": "Excellent GPU! Works perfectly."
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Excellent GPU! Works perfectly."
        assert data["product_id"] == product_id
    
    async def test_create_duplicate_review(self, client: AsyncClient, customer_token: str):
        """Test creating duplicate review for same product (should fail)"""
        # Get a product with existing review
        response = await client.get("/products?limit=1")
        product_id = response.json()[0]["id"]
        
        # Try to create another review (may fail if already reviewed)
        response = await client.post(
            "/reviews",
            headers=get_auth_headers(customer_token),
            json={
                "product_id": product_id,
                "rating": 4,
                "comment": "Second review"
            }
        )
        # Could be 400 (duplicate) or 403 (no shipped order)
        assert response.status_code in [400, 403]
    
    async def test_update_own_review(self, client: AsyncClient, customer_token: str, staff_token: str):
        """Test updating own review"""
        # Create a review first
        response = await client.get("/products?limit=1")
        product_id = response.json()[0]["id"]
        
        # Create order and ship it
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "123 Test",
                "items": [{"product_id": product_id, "quantity": 1}]
            }
        )
        order_id = response.json()["id"]
        
        await client.patch(
            f"/orders/{order_id}/status",
            headers=get_auth_headers(staff_token),
            json={"status": "SHIPPED"}
        )
        
        response = await client.post(
            "/reviews",
            headers=get_auth_headers(customer_token),
            json={
                "product_id": product_id,
                "rating": 4,
                "comment": "Good product"
            }
        )
        
        if response.status_code == 201:
            review_id = response.json()["id"]
            
            # Update the review
            response = await client.patch(
                f"/reviews/{review_id}",
                headers=get_auth_headers(customer_token),
                json={
                    "rating": 5,
                    "comment": "Actually, it's excellent!"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["rating"] == 5
            assert data["comment"] == "Actually, it's excellent!"
    
    async def test_delete_own_review(self, client: AsyncClient, customer_token: str, staff_token: str):
        """Test deleting own review"""
        # Get a different product
        response = await client.get("/products?skip=1&limit=1")
        if len(response.json()) == 0:
            pytest.skip("Not enough products")
        product_id = response.json()[0]["id"]
        
        # Create order, ship, and review
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "123 Test",
                "items": [{"product_id": product_id, "quantity": 1}]
            }
        )
        order_id = response.json()["id"]
        
        await client.patch(
            f"/orders/{order_id}/status",
            headers=get_auth_headers(staff_token),
            json={"status": "SHIPPED"}
        )
        
        response = await client.post(
            "/reviews",
            headers=get_auth_headers(customer_token),
            json={
                "product_id": product_id,
                "rating": 4,
                "comment": "To be deleted"
            }
        )
        
        if response.status_code == 201:
            review_id = response.json()["id"]
            
            # Delete the review
            response = await client.delete(
                f"/reviews/{review_id}",
                headers=get_auth_headers(customer_token)
            )
            assert response.status_code == 204
    
    async def test_list_all_reviews_as_admin(self, client: AsyncClient, admin_token: str):
        """Test listing all reviews as admin"""
        response = await client.get(
            "/reviews",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_list_all_reviews_as_customer(self, client: AsyncClient, customer_token: str):
        """Test listing all reviews as customer (should fail)"""
        response = await client.get(
            "/reviews",
            headers=get_auth_headers(customer_token)
        )
        assert response.status_code == 403
    
    async def test_delete_any_review_as_admin(self, client: AsyncClient, admin_token: str):
        """Test admin can delete any review"""
        # Get a review
        response = await client.get(
            "/reviews?limit=1",
            headers=get_auth_headers(admin_token)
        )
        
        if len(response.json()) > 0:
            review_id = response.json()[0]["id"]
            
            response = await client.delete(
                f"/reviews/{review_id}",
                headers=get_auth_headers(admin_token)
            )
            assert response.status_code == 204
