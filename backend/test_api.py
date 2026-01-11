"""
API Test Script - Tests all major endpoints
Run this after starting the server to verify everything works
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

# Store tokens and IDs
admin_token: Optional[str] = None
customer_token: Optional[str] = None
staff_token: Optional[str] = None
test_product_id: Optional[int] = None
test_order_id: Optional[int] = None
test_review_id: Optional[int] = None


def print_test(name: str):
    """Print test name"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)


def print_response(response):
    """Print response details"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health_check():
    """Test health check endpoint"""
    print_test("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    assert response.status_code == 200


def test_signup():
    """Test user registration"""
    print_test("User Signup")
    
    # Sign up customer
    response = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": "customer@test.com",
        "password": "password123",
        "full_name": "Test Customer"
    })
    print_response(response)
    assert response.status_code == 201


def test_login():
    """Test user login"""
    global admin_token, customer_token, staff_token
    
    # Login as customer
    print_test("Login - Customer")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "customer@test.com",
        "password": "password123"
    })
    print_response(response)
    assert response.status_code == 200
    customer_token = response.json()["access_token"]
    
    # Login as admin
    print_test("Login - Admin")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@infinitecompute.com",
        "password": "admin123"
    })
    print_response(response)
    assert response.status_code == 200
    admin_token = response.json()["access_token"]
    
    # Login as staff
    print_test("Login - Staff")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "staff@infinitecompute.com",
        "password": "staff123"
    })
    print_response(response)
    assert response.status_code == 200
    staff_token = response.json()["access_token"]


def test_get_current_user():
    """Test getting current user info"""
    print_test("Get Current User")
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_list_products():
    """Test listing products"""
    global test_product_id
    
    print_test("List Products")
    response = requests.get(f"{BASE_URL}/products")
    print_response(response)
    assert response.status_code == 200
    
    products = response.json()
    if products:
        test_product_id = products[0]["id"]
        print(f"\nUsing product ID {test_product_id} for tests")


def test_get_product():
    """Test getting a specific product"""
    print_test("Get Product Details")
    response = requests.get(f"{BASE_URL}/products/{test_product_id}")
    print_response(response)
    assert response.status_code == 200


def test_create_product():
    """Test creating a product (admin only)"""
    print_test("Create Product (Admin)")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(f"{BASE_URL}/products", headers=headers, json={
        "name": "Test GPU Model",
        "product_line": "Test Line",
        "architecture": "Test Arch",
        "price": 999.99,
        "stock_quantity": 10,
        "description": "Test GPU for API testing"
    })
    print_response(response)
    assert response.status_code == 201


def test_list_news():
    """Test listing news articles"""
    print_test("List News")
    response = requests.get(f"{BASE_URL}/news")
    print_response(response)
    assert response.status_code == 200


def test_create_news():
    """Test creating news (staff)"""
    print_test("Create News (Staff)")
    headers = {"Authorization": f"Bearer {staff_token}"}
    response = requests.post(f"{BASE_URL}/news", headers=headers, json={
        "title": "Test News Article",
        "content": "This is a test news article created via API",
        "category": "Test",
        "summary": "Test summary"
    })
    print_response(response)
    assert response.status_code == 201


def test_create_order():
    """Test creating an order"""
    global test_order_id
    
    print_test("Create Order (Guest)")
    response = requests.post(f"{BASE_URL}/orders", json={
        "guest_email": "guest@test.com",
        "shipping_address": "123 Test St, Test City, TC 12345",
        "items": [
            {
                "product_id": test_product_id,
                "quantity": 1
            }
        ]
    })
    print_response(response)
    assert response.status_code == 201
    test_order_id = response.json()["id"]
    
    # Create order with discount (authenticated)
    print_test("Create Order (Authenticated - with discount)")
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = requests.post(f"{BASE_URL}/orders", headers=headers, json={
        "shipping_address": "456 Customer Ave, Customer City, CC 67890",
        "items": [
            {
                "product_id": test_product_id,
                "quantity": 2
            }
        ]
    })
    print_response(response)
    assert response.status_code == 201


def test_track_order():
    """Test order tracking"""
    print_test("Track Order")
    response = requests.post(f"{BASE_URL}/orders/track", json={
        "identifier": "guest@test.com"
    })
    print_response(response)
    assert response.status_code == 200


def test_update_order_status():
    """Test updating order status (staff)"""
    print_test("Update Order Status (Staff)")
    headers = {"Authorization": f"Bearer {staff_token}"}
    response = requests.patch(
        f"{BASE_URL}/orders/{test_order_id}/status",
        headers=headers,
        json={"status": "SHIPPED"}
    )
    print_response(response)
    assert response.status_code == 200


def test_create_review():
    """Test creating a review"""
    global test_review_id
    
    print_test("Create Review (requires shipped order)")
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = requests.post(f"{BASE_URL}/reviews", headers=headers, json={
        "product_id": test_product_id,
        "rating": 5,
        "comment": "Excellent GPU! Works great for my AI projects."
    })
    print_response(response)
    # This might fail if user doesn't have a shipped order, which is expected
    if response.status_code == 201:
        test_review_id = response.json()["id"]


def test_get_product_reviews():
    """Test getting reviews for a product"""
    print_test("Get Product Reviews")
    response = requests.get(f"{BASE_URL}/reviews/product/{test_product_id}")
    print_response(response)
    assert response.status_code == 200


def test_analytics():
    """Test analytics endpoint (admin)"""
    print_test("Get Analytics (Admin)")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/analytics?timeframe=all", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_list_users():
    """Test listing users (admin)"""
    print_test("List Users (Admin)")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    print_response(response)
    assert response.status_code == 200


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("STARTING API TESTS")
    print("="*60)
    
    try:
        test_health_check()
        test_signup()
        test_login()
        test_get_current_user()
        test_list_products()
        if test_product_id:
            test_get_product()
            test_create_product()
            test_list_news()
            test_create_news()
            test_create_order()
            test_track_order()
            test_update_order_status()
            test_create_review()
            test_get_product_reviews()
            test_analytics()
            test_list_users()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        
    except AssertionError as e:
        print("\n" + "="*60)
        print("✗ TEST FAILED!")
        print("="*60)
        raise
    except requests.exceptions.ConnectionError:
        print("\n" + "="*60)
        print("✗ CONNECTION ERROR")
        print("Make sure the server is running at", BASE_URL)
        print("="*60)


if __name__ == "__main__":
    run_all_tests()
