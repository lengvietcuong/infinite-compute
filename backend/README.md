# InfiniteCompute Backend API

FastAPI backend for the InfiniteCompute e-commerce platform.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/infinitecompute
SECRET_KEY=your-secret-key-here-change-in-production
OPEN_ROUTER_API_KEY=your-openrouter-api-key-here
```

### 3. Create PostgreSQL Database

```bash
createdb infinitecompute
```

Or using psql:

```sql
CREATE DATABASE infinitecompute;
```

### 4. Initialize Database

Run the SQL schema first:

```bash
psql infinitecompute < database/database.sql
```

Then load initial data:

```bash
python -m database.initialize_database
```

## Running the Application

```bash
uvicorn main:app --reload
```

## Testing

The backend uses `pytest` for testing.

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=.
```

### Run specific test files

```bash
pytest tests/test_auth.py
```

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token

### Users

- `GET /users/me` - Get current user info
- `GET /users` - List all users (Admin)
- `GET /users/{id}` - Get user by ID (Admin)
- `PATCH /users/{id}` - Update user (Admin)
- `DELETE /users/{id}` - Delete user (Admin)

### Products

- `GET /products` - List all products (with filters)
- `GET /products/{id}` - Get product details
- `POST /products` - Create product (Admin)
- `PATCH /products/{id}` - Update product (Admin)
- `DELETE /products/{id}` - Delete product (Admin)

### News

- `GET /news` - List all news articles
- `GET /news/{id}` - Get news article
- `POST /news` - Create news (Staff/Admin)
- `PATCH /news/{id}` - Update news (Staff/Admin)
- `DELETE /news/{id}` - Delete news (Admin)

### Orders

- `POST /orders` - Create new order
- `GET /orders/my-orders` - Get current user's orders
- `POST /orders/track` - Track orders by email/ID/tracking number
- `GET /orders` - List all orders (Staff/Admin)
- `PATCH /orders/{id}/status` - Update order status (Staff/Admin)

### Reviews

- `GET /reviews/product/{id}` - Get reviews for a product
- `POST /reviews` - Create review (requires shipped order)
- `PATCH /reviews/{id}` - Update own review
- `DELETE /reviews/{id}` - Delete own review or any (Admin)
- `GET /reviews` - List all reviews (Admin)

### Analytics

- `GET /analytics?timeframe={period}` - Get analytics data (Admin)
  - Timeframes: `today`, `7d`, `30d`, `90d`, `365d`, `all`

## User Roles

- **Customer**: Default role for registered users

  - Place orders with discount
  - Leave reviews on shipped products
  - Access chat history
  - Track orders

- **Staff**: Can manage operations

  - All customer permissions
  - Create/edit news articles
  - Update order status
  - Update inventory

- **Admin**: Full access
  - All staff permissions
  - CRUD operations on users, products, reviews
  - View analytics dashboard
  - Delete news articles

## Features

### Authentication

- JWT-based authentication
- Secure password hashing with bcrypt
- Role-based access control

### Orders

- Automatic inventory management
- 10% discount for authenticated users
- Order tracking by email, ID, or tracking number
- Order statuses: PAID, SHIPPED, DELIVERED, CANCELLED

### Reviews

- Only users with shipped orders can review products
- One review per user per product
- 1-5 star rating with optional comment
- Users can edit/delete their own reviews

### Analytics (Admin Only)

- Revenue tracking
- Total orders
- Average order value
- Top products by units sold
- Top products by revenue
- Multiple timeframe options

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── auth.py                # Authentication utilities
├── schemas.py             # Pydantic models
├── requirements.txt       # Python dependencies
├── database/
│   ├── database.py        # Database connection
│   ├── database.sql       # SQL schema
│   ├── models.py          # SQLAlchemy models
│   └── initialize_database.py
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── products.py
│   ├── news.py
│   ├── orders.py
│   ├── reviews.py
│   └── analytics.py
└── data/
    ├── gpus.csv
    └── news.csv
```
