import pytest
import uuid
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints"""
    
    async def test_signup_new_user(self, client: AsyncClient):
        """Test user registration"""
        unique_email = f"newuser{uuid.uuid4().hex[:8]}@test.com"
        response = await client.post("/auth/signup", json={
            "email": unique_email,
            "password": "password123",
            "full_name": "New Test User"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == unique_email
        assert data["full_name"] == "New Test User"
        assert data["role"] == "customer"
        assert "id" in data
        assert "coupon_code" in data
        assert "coupon_discount" in data
        assert float(data["coupon_discount"]) == 10.0
        pytest.test_counter += 1
    
    async def test_signup_duplicate_email(self, client: AsyncClient):
        """Test signup with duplicate email"""
        response = await client.post("/auth/signup", json={
            "email": "customer@gmail.com",
            "password": "password123",
            "full_name": "Duplicate User"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_login_success(self, client: AsyncClient):
        """Test successful login"""
        response = await client.post("/auth/login", json={
            "email": "customer@gmail.com",
            "password": "test"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password"""
        response = await client.post("/auth/login", json={
            "email": "customer@gmail.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post("/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password123"
        })
        assert response.status_code == 401


# Initialize counter for unique emails
pytest.test_counter = 0
