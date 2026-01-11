import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestUsers:
    """Test user management endpoints"""
    
    async def test_get_current_user(self, client: AsyncClient, customer_token: str):
        """Test getting current user info"""
        response = await client.get(
            "/users/me",
            headers=get_auth_headers(customer_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "customer@gmail.com"
        assert data["role"] == "customer"
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without auth"""
        response = await client.get("/users/me")
        assert response.status_code == 403
    
    async def test_list_users_as_admin(self, client: AsyncClient, admin_token: str):
        """Test listing users as admin"""
        response = await client.get(
            "/users",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_list_users_as_customer(self, client: AsyncClient, customer_token: str):
        """Test listing users as customer (should fail)"""
        response = await client.get(
            "/users",
            headers=get_auth_headers(customer_token)
        )
        assert response.status_code == 403
    
    async def test_list_users_by_role(self, client: AsyncClient, admin_token: str):
        """Test filtering users by role"""
        response = await client.get(
            "/users?role=customer",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        for user in data:
            assert user["role"] == "customer"
    
    async def test_get_user_by_id(self, client: AsyncClient, admin_token: str):
        """Test getting specific user by ID"""
        # First get list of users
        response = await client.get(
            "/users",
            headers=get_auth_headers(admin_token)
        )
        users = response.json()
        user_id = users[0]["id"]
        
        # Get specific user
        response = await client.get(
            f"/users/{user_id}",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
    
    async def test_update_user(self, client: AsyncClient, admin_token: str):
        """Test updating user"""
        # Get a user to update
        response = await client.get(
            "/users?role=customer&limit=1",
            headers=get_auth_headers(admin_token)
        )
        users = response.json()
        user_id = users[0]["id"]
        
        # Update user
        response = await client.patch(
            f"/users/{user_id}",
            headers=get_auth_headers(admin_token),
            json={"full_name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    async def test_delete_user(self, client: AsyncClient, admin_token: str):
        """Test deleting user"""
        # Create a new user to delete
        response = await client.post("/auth/signup", json={
            "email": f"todelete{pytest.test_counter}@test.com",
            "password": "password123",
            "full_name": "To Delete"
        })
        pytest.test_counter += 1
        user_id = response.json()["id"]
        
        # Delete the user
        response = await client.delete(
            f"/users/{user_id}",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 204
        
        # Verify user is deleted
        response = await client.get(
            f"/users/{user_id}",
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 404


pytest.test_counter = 1000
