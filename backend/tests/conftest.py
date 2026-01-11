import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture(scope="session")
async def client():
    """Create an async HTTP client for testing"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def admin_token(client):
    """Get admin authentication token"""
    response = await client.post("/auth/login", json={
        "email": "admin@gmail.com",
        "password": "test"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
async def staff_token(client):
    """Get staff authentication token"""
    response = await client.post("/auth/login", json={
        "email": "staff@gmail.com",
        "password": "test"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
async def customer_token(client):
    """Get customer authentication token"""
    response = await client.post("/auth/login", json={
        "email": "customer@gmail.com",
        "password": "test"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
async def test_product_id(client):
    """Get a test product ID"""
    response = await client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    return products[0]["id"]


def get_auth_headers(token: str) -> dict:
    """Helper to create authorization headers"""
    return {"Authorization": f"Bearer {token}"}
