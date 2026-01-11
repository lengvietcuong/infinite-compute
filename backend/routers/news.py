from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, asc, desc, func
from typing import List, Optional
from datetime import date
from math import ceil
from database.database import get_db
from database.models import News, User
from schemas import NewsResponse, NewsCreate, NewsUpdate, PaginatedNewsResponse
from auth import get_current_staff, get_current_admin

router = APIRouter(prefix="/news", tags=["News"])


@router.get("", response_model=PaginatedNewsResponse)
async def list_news(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("recent", pattern="^(recent|oldest)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all news articles with filtering, searching, and sorting"""
    query = select(News)
    
    # Filtering by category
    if category:
        query = query.where(News.category == category)
    
    # Searching (title, content, category)
    if search:
        search_filter = or_(
            News.title.ilike(f"%{search}%"),
            News.content.ilike(f"%{search}%"),
            News.category.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Date Range Filtering
    if start_date:
        query = query.where(News.published_date >= start_date)
    if end_date:
        query = query.where(News.published_date <= end_date)
    
    # Get total count with the same filters
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Sorting
    if sort_by == "oldest":
        query = query.order_by(News.published_date.asc(), News.created_at.asc())
    else:  # recent
        query = query.order_by(News.published_date.desc(), News.created_at.desc())
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    news_articles = result.scalars().all()
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = ceil(total / limit) if limit > 0 else 1
    
    return PaginatedNewsResponse(
        items=news_articles,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific news article by ID"""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found"
        )
    
    return news


@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    news_data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Create a new news article (Staff/Admin only)"""
    new_news = News(**news_data.model_dump())
    db.add(new_news)
    await db.commit()
    await db.refresh(new_news)
    
    return new_news


@router.patch("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_data: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Update a news article (Staff/Admin only)"""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found"
        )
    
    # Update fields
    update_data = news_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(news, field, value)
    
    await db.commit()
    await db.refresh(news)
    
    return news


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a news article (Admin only)"""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found"
        )
    
    await db.delete(news)
    await db.commit()
    
    return None
