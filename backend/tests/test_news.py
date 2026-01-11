import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestNews:
    """Test news endpoints"""
    
    async def test_list_news(self, client: AsyncClient):
        """Test listing all news"""
        response = await client.get("/news")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        
        # Check news structure
        article = data["items"][0]
        assert "id" in article
        assert "title" in article
        assert "content" in article
    
    async def test_list_news_by_category(self, client: AsyncClient):
        """Test filtering news by category"""
        response = await client.get("/news?category=AI Hardware")
        assert response.status_code == 200
        data = response.json()
        for article in data["items"]:
            assert article["category"] == "AI Hardware"
    
    async def test_pagination_metadata(self, client: AsyncClient):
        """Test pagination metadata is correct"""
        response = await client.get("/news?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total"] > 0
        assert data["total_pages"] > 0
        
        # Verify total_pages calculation
        expected_pages = (data["total"] + 4) // 5  # ceil(total / 5)
        assert data["total_pages"] == expected_pages
        
        # Test second page
        response = await client.get("/news?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
    
    async def test_get_news_by_id(self, client: AsyncClient):
        """Test getting specific news article"""
        # Get first news ID
        response = await client.get("/news?limit=1")
        news_id = response.json()["items"][0]["id"]
        
        response = await client.get(f"/news/{news_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == news_id
    
    async def test_get_nonexistent_news(self, client: AsyncClient):
        """Test getting non-existent news"""
        response = await client.get("/news/999999")
        assert response.status_code == 404
    
    async def test_create_news_as_staff(self, client: AsyncClient, staff_token: str):
        """Test creating news as staff"""
        response = await client.post(
            "/news",
            headers=get_auth_headers(staff_token),
            json={
                "title": f"Test News Article {pytest.news_counter}",
                "content": "This is test news content created via API testing.",
                "category": "Test",
                "summary": "Test summary"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == f"Test News Article {pytest.news_counter}"
        pytest.news_counter += 1
    
    async def test_create_news_as_admin(self, client: AsyncClient, admin_token: str):
        """Test creating news as admin"""
        response = await client.post(
            "/news",
            headers=get_auth_headers(admin_token),
            json={
                "title": f"Admin News {pytest.news_counter}",
                "content": "News created by admin.",
                "category": "Admin",
                "summary": "Admin test"
            }
        )
        assert response.status_code == 201
        pytest.news_counter += 1
    
    async def test_create_news_as_customer(self, client: AsyncClient, customer_token: str):
        """Test creating news as customer (should fail)"""
        response = await client.post(
            "/news",
            headers=get_auth_headers(customer_token),
            json={
                "title": "Unauthorized News",
                "content": "This should not work.",
                "category": "Test"
            }
        )
        assert response.status_code == 403
    
    async def test_update_news_as_staff(self, client: AsyncClient, staff_token: str):
        """Test updating news as staff"""
        # Create news first
        response = await client.post(
            "/news",
            headers=get_auth_headers(staff_token),
            json={
                "title": "To Update",
                "content": "Original content",
                "category": "Test"
            }
        )
        news_id = response.json()["id"]
        
        # Update it
        response = await client.patch(
            f"/news/{news_id}",
            headers=get_auth_headers(staff_token),
            json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    async def test_delete_news_as_admin(self, client: AsyncClient, admin_token: str):
        """Test deleting news as admin"""
        # Create news
        response = await client.post(
            "/news",
            headers=get_auth_headers(admin_token),
            json={
                "title": "To Delete",
                "content": "Will be deleted",
                "category": "Test"
            }
        )
        news_id = response.json()["id"]
        
        # Delete it
        response = await client.delete(
            f"/news/{news_id}",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 204
    
    async def test_delete_news_as_staff(self, client: AsyncClient, staff_token: str):
        """Test deleting news as staff (should fail)"""
        # Get a news ID
        response = await client.get("/news?limit=1")
        news_id = response.json()["items"][0]["id"]
        
        response = await client.delete(
            f"/news/{news_id}",
            headers=get_auth_headers(staff_token)
        )
        assert response.status_code == 403


pytest.news_counter = 1
