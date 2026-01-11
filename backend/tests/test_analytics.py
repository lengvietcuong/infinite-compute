import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestAnalytics:
    """Test analytics endpoints"""
    
    async def test_get_analytics_all_time(self, client: AsyncClient, admin_token: str):
        """Test getting analytics for all time"""
        response = await client.get(
            "/analytics?timeframe=all",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "revenue" in data
        assert "total_orders" in data
        assert "average_order_value" in data
        assert "top_products_units" in data
        assert "top_products_revenue" in data
        
        # Check types
        assert isinstance(data["top_products_units"], list)
        assert isinstance(data["top_products_revenue"], list)
    
    async def test_get_analytics_today(self, client: AsyncClient, admin_token: str):
        """Test getting analytics for today"""
        response = await client.get(
            "/analytics?timeframe=today",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
        assert "total_orders" in data
    
    async def test_get_analytics_7_days(self, client: AsyncClient, admin_token: str):
        """Test getting analytics for last 7 days"""
        response = await client.get(
            "/analytics?timeframe=7d",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
    
    async def test_get_analytics_30_days(self, client: AsyncClient, admin_token: str):
        """Test getting analytics for last 30 days"""
        response = await client.get(
            "/analytics?timeframe=30d",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
    
    async def test_get_analytics_90_days(self, client: AsyncClient, admin_token: str):
        """Test getting analytics for last 90 days"""
        response = await client.get(
            "/analytics?timeframe=90d",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
    
    async def test_get_analytics_365_days(self, client: AsyncClient, admin_token: str):
        """Test getting analytics for last 365 days"""
        response = await client.get(
            "/analytics?timeframe=365d",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
    
    async def test_get_analytics_as_customer(self, client: AsyncClient, customer_token: str):
        """Test getting analytics as customer (should fail)"""
        response = await client.get(
            "/analytics",
            headers=get_auth_headers(customer_token)
        )
        assert response.status_code == 403
    
    async def test_get_analytics_as_staff(self, client: AsyncClient, staff_token: str):
        """Test getting analytics as staff (should fail)"""
        response = await client.get(
            "/analytics",
            headers=get_auth_headers(staff_token)
        )
        assert response.status_code == 403
    
    async def test_analytics_top_products_structure(self, client: AsyncClient, admin_token: str):
        """Test that top products have correct structure"""
        response = await client.get(
            "/analytics?timeframe=all",
            headers=get_auth_headers(admin_token)
        )
        data = response.json()
        
        # Check top products by units
        if len(data["top_products_units"]) > 0:
            product = data["top_products_units"][0]
            assert "product_id" in product
            assert "product_name" in product
            assert "units_sold" in product
        
        # Check top products by revenue
        if len(data["top_products_revenue"]) > 0:
            product = data["top_products_revenue"][0]
            assert "product_id" in product
            assert "product_name" in product
            assert "revenue" in product
