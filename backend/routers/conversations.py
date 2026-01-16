from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from database.database import get_db
from database.models import ChatSession, ChatMessage, User, ChatRole
from auth import get_current_staff


router = APIRouter(prefix="/conversations", tags=["conversations"])


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    user_id: int | None
    user_name: str | None
    user_email: str | None
    message_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: str
    user_id: int | None
    user_name: str | None
    user_email: str | None
    created_at: str
    updated_at: str
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


@router.get("", response_model=List[ConversationResponse])
async def get_all_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
    skip: int = 0,
    limit: int = 100,
    user_only: bool = False,
    guest_only: bool = False,
):
    """Get all conversations with optional filters (Admin and Staff only)"""
    query = select(ChatSession)
    
    if user_only:
        query = query.where(ChatSession.user_id.isnot(None))
    elif guest_only:
        query = query.where(ChatSession.user_id.is_(None))
    
    query = query.order_by(ChatSession.updated_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    conversations = []
    for session in sessions:
        user_name = None
        user_email = None
        
        if session.user_id:
            user_result = await db.execute(
                select(User).where(User.id == session.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user_name = user.full_name
                user_email = user.email
        
        message_count_result = await db.execute(
            select(func.count(ChatMessage.id)).where(ChatMessage.chat_id == session.id)
        )
        message_count = message_count_result.scalar()
        
        conversations.append(
            ConversationResponse(
                id=str(session.id),
                user_id=session.user_id,
                user_name=user_name,
                user_email=user_email,
                message_count=message_count,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
            )
        )
    
    return conversations


@router.get("/stats")
async def get_conversation_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Get conversation statistics (Admin and Staff only)"""
    total_count_result = await db.execute(select(func.count(ChatSession.id)))
    total_count = total_count_result.scalar()
    
    user_count_result = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.user_id.isnot(None))
    )
    user_count = user_count_result.scalar()
    
    total_messages_result = await db.execute(select(func.count(ChatMessage.id)))
    total_messages = total_messages_result.scalar()
    
    return {
        "total_conversations": total_count,
        "user_conversations": user_count,
        "guest_conversations": total_count - user_count,
        "total_messages": total_messages,
    }


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Get a specific conversation with all messages (Admin and Staff only)"""
    try:
        conversation_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == conversation_uuid)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    user_name = None
    user_email = None
    
    if session.user_id:
        user_result = await db.execute(
            select(User).where(User.id == session.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user_name = user.full_name
            user_email = user.email
    
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    messages = messages_result.scalars().all()
    
    message_responses = [
        MessageResponse(
            id=msg.id,
            role=msg.role.value,
            content=msg.content,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]
    
    return ConversationDetailResponse(
        id=str(session.id),
        user_id=session.user_id,
        user_name=user_name,
        user_email=user_email,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        messages=message_responses,
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """Delete a conversation (Admin and Staff only)"""
    try:
        conversation_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == conversation_uuid)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(session)
    await db.commit()
    
    return None
