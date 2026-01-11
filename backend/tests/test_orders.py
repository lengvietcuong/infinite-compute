import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestOrders:
    """Test order endpoints"""
    
    async def test_create_order_as_guest(self, client: AsyncClient, test_product_id: int):
        """Test creating order as guest"""
        response = await client.post(
            "/orders",
            json={
                "guest_email": f"guest{pytest.order_counter}@test.com",
                "shipping_address": "123 Test St, Test City, TC 12345",
                "items": [
                    {
                        "product_id": test_product_id,
                        "quantity": 1
                    }
                ]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["guest_email"] == f"guest{pytest.order_counter}@test.com"
        assert data["status"] == "PAID"
        assert "tracking_number" in data
        assert len(data["items"]) == 1
        pytest.order_counter += 1
    
    async def test_create_order_as_customer_with_discount(self, client: AsyncClient, customer_token: str, test_product_id: int):
        """Test creating order as authenticated user (with discount)"""
        # Get product price first
        response = await client.get(f"/products/{test_product_id}")
        product = response.json()
        original_price = float(product["price"])
        
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "456 Customer Ave, Customer City, CC 67890",
                "items": [
                    {
                        "product_id": test_product_id,
                        "quantity": 1
                    }
                ]
            }
        )
        assert response.status_code == 201
        data = response.json()
        
        # Verify discount applied (10% off)
        expected_total = original_price * 0.9
        actual_total = float(data["total_amount"])
        assert abs(actual_total - expected_total) < 0.01
    
    async def test_create_order_multiple_items(self, client: AsyncClient, customer_token: str):
        """Test creating order with multiple items"""
        # Get multiple products
        response = await client.get("/products?limit=3")
        products = response.json()
        
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "789 Multi Ave, Multi City, MC 11111",
                "items": [
                    {"product_id": products[0]["id"], "quantity": 1},
                    {"product_id": products[1]["id"], "quantity": 2}
                ]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 2
    
    async def test_create_order_insufficient_stock(self, client: AsyncClient, customer_token: str):
        """Test creating order with insufficient stock"""
        # Get a product
        response = await client.get("/products?limit=1")
        product_id = response.json()[0]["id"]
        
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "123 Test St",
                "items": [
                    {"product_id": product_id, "quantity": 99999}
                ]
            }
        )
        assert response.status_code == 400
        assert "insufficient stock" in response.json()["detail"].lower()
    
    async def test_create_order_nonexistent_product(self, client: AsyncClient, customer_token: str):
        """Test creating order with non-existent product"""
        response = await client.post(
            "/orders",
            headers=get_auth_headers(customer_token),
            json={
                "shipping_address": "123 Test St",
                "items": [
                    {"product_id": 999999, "quantity": 1}
                ]
            }
        )
        assert response.status_code == 404
    
    async def test_get_my_orders(self, client: AsyncClient, customer_token: str):
        """Test getting current user's orders"""
        response = await client.get(
            "/orders/my-orders",
            headers=get_auth_headers(customer_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_track_order_by_email(self, client: AsyncClient):
        """Test tracking order by email"""
        # Create an order first
        response = await client.post(
            "/orders",
            json={
                "guest_email": f"track{pytest.order_counter}@test.com",
                "shipping_address": "123 Track St",
                "items": [{"product_id": 1, "quantity": 1}]
            }
        )
        pytest.order_counter += 1
        guest_email = response.json()["guest_email"]
        
        # Track it
        response = await client.post(
            "/orders/track",
            json={"identifier": guest_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_track_order_by_tracking_number(self, client: AsyncClient):
        """Test tracking order by tracking number"""
        # Create an order
        response = await client.post(
            "/orders",
            json={
                "guest_email": f"track2{pytest.order_counter}@test.com",
                "shipping_address": "123 Track St",
                "items": [{"product_id": 1, "quantity": 1}]
            }
        )
        pytest.order_counter += 1
        tracking_number = response.json()["tracking_number"]
        
        # Track by tracking number
        response = await client.post(
            "/orders/track",
            json={"identifier": tracking_number}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    async def test_track_order_not_found(self, client: AsyncClient):
        """Test tracking non-existent order"""
        response = await client.post(
            "/orders/track",
            json={"identifier": "nonexistent@test.com"}
        )
        assert response.status_code == 404
    
    async def test_list_all_orders_as_staff(self, client: AsyncClient, staff_token: str):
        """Test listing all orders as staff"""
        response = await client.get(
            "/orders",
            headers=get_auth_headers(staff_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_list_all_orders_as_customer(self, client: AsyncClient, customer_token: str):
        """Test listing all orders as customer (should fail)"""
        response = await client.get(
            "/orders",
            headers=get_auth_headers(customer_token)
        )
        assert response.status_code == 403
    
    async def test_filter_orders_by_status(self, client: AsyncClient, staff_token: str):
        """Test filtering orders by status"""
        response = await client.get(
            "/orders?status=PAID",
            headers=get_auth_headers(staff_token)
        )
        assert response.status_code == 200
        data = response.json()
        for order in data:
            assert order["status"] == "PAID"
    
    async def test_update_order_status_as_staff(self, client: AsyncClient, staff_token: str):
        """Test updating order status as staff"""
        # Get an order
        response = await client.get(
            "/orders?limit=1",
            headers=get_auth_headers(staff_token)
        )
        order_id = response.json()[0]["id"]
        
        # Update status
        response = await client.patch(
            f"/orders/{order_id}/status",
            headers=get_auth_headers(staff_token),
            json={"status": "SHIPPED"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SHIPPED"
    
    async def test_update_order_status_as_customer(self, client: AsyncClient, customer_token: str):
        """Test updating order status as customer (should fail)"""
        response = await client.patch(
            "/orders/1/status",
            headers=get_auth_headers(customer_token),
            json={"status": "SHIPPED"}
        )
        assert response.status_code == 403


pytest.order_counter = 1
