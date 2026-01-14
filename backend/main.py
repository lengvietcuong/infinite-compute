from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from routers import auth, users, products, news, orders, reviews, analytics


app = FastAPI(
    title="InfiniteCompute API",
    description="AI-powered e-commerce platform for NVIDIA GPUs",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(news.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Welcome to InfiniteCompute API",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
