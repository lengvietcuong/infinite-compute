from typing import Optional
import uuid
import logging
import asyncio
import json

import aiohttp
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel

from database.database import AsyncSessionLocal
from database.models import ChatSession, ChatMessage, User, ChatRole
from auth import get_current_user_optional
from rag.inference import get_llm_response, stream_llm_response, embed, Message
from rag.retrieval.chunk_retrieval import semantic_search
from config import SYSTEM_PROMPT, MAX_CONCURRENT_REQUESTS


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    chat_id: str | None = None


async def _get_or_create_chat(db: AsyncSession, current_user: Optional[User], chat_id_str: Optional[str]) -> ChatSession:
    if current_user:
        result = await db.execute(
            select(ChatSession).where(ChatSession.user_id == current_user.id)
        )
        chat = result.scalars().first()
        if chat:
            return chat
        
        chat = ChatSession(user_id=current_user.id)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat
    
    if chat_id_str:
        try:
            chat_uuid = uuid.UUID(chat_id_str)
            result = await db.execute(
                select(ChatSession).where(ChatSession.id == chat_uuid)
            )
            chat = result.scalars().first()
            if chat:
                return chat
        except ValueError:
            pass
            
    chat = ChatSession(user_id=None)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


@router.post("")
async def chat(
    request: ChatRequest,
    current_user: User | None = Depends(get_current_user_optional),
):
    logger.info(f"Chat request received: message length={len(request.message)}")
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with AsyncSessionLocal() as db, aiohttp.ClientSession() as http_session:
        chat = await _get_or_create_chat(db, current_user, request.chat_id)
        logger.info(f"Chat ID: {chat.id}")

        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at)
        )
        db_messages = result.scalars().all()
        logger.info(f"Loaded {len(db_messages)} previous messages")
        
        user_msg = ChatMessage(
            chat_id=chat.id,
            role=ChatRole.USER,
            content=request.message
        )
        db.add(user_msg)
        await db.commit()
        
        query_embedding = await embed(
            text=request.message,
            http_session=http_session,
            semaphore=semaphore,
        )
        context = await semantic_search(query_embedding=query_embedding)
        logger.info(f"Context from semantic search: {context or '(None)'}")

        messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in db_messages:
            messages.append({"role": msg.role.value, "content": msg.content})
        
        user_content = request.message
        if context:
            user_content += f"\n\n---\n\nPotentially relevant information:\n{context}"
        
        messages.append({"role": "user", "content": user_content})
        
        messages = await get_llm_response(
            messages=messages,
            query_embedding=query_embedding,
            http_session=http_session,
            semaphore=semaphore,
        )
        
        response_content = messages[-1]["content"]
        assistant_msg = ChatMessage(
            chat_id=chat.id,
            role=ChatRole.ASSISTANT,
            content=response_content
        )
        db.add(assistant_msg)
        await db.commit()
        
        return {
            "response": response_content,
            "chat_id": str(chat.id)
        }


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Streaming chat endpoint that returns Server-Sent Events (SSE).
    """
    async def event_generator():
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async with AsyncSessionLocal() as db, aiohttp.ClientSession() as http_session:
            try:
                chat = await _get_or_create_chat(db, current_user, request.chat_id)
                logger.info(f"Streaming chat ID: {chat.id}")
                
                # Send chat_id immediately
                yield f"data: {json.dumps({'type': 'chat_id', 'chat_id': str(chat.id)})}\n\n"

                result = await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.chat_id == chat.id)
                    .order_by(ChatMessage.created_at)
                )
                db_messages = result.scalars().all()
                logger.info(f"Loaded {len(db_messages)} previous messages")
                
                user_msg = ChatMessage(
                    chat_id=chat.id,
                    role=ChatRole.USER,
                    content=request.message
                )
                db.add(user_msg)
                await db.commit()
                
                query_embedding = await embed(
                    text=request.message,
                    http_session=http_session,
                    semaphore=semaphore,
                )
                context = await semantic_search(query_embedding=query_embedding)
                logger.info(f"Context from semantic search: {context or '(None)'}")

                messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in db_messages:
                    messages.append({"role": msg.role.value, "content": msg.content})
                
                user_content = request.message
                if context:
                    user_content += f"\n\n---\n\nPotentially relevant information:\n{context}"
                
                messages.append({"role": "user", "content": user_content})
                
                full_response = ""
                
                async for event in stream_llm_response(
                    messages=messages,
                    query_embedding=query_embedding,
                    http_session=http_session,
                    semaphore=semaphore,
                ):
                    if event["type"] == "content":
                        full_response += event["content"]
                    
                    yield f"data: {json.dumps(event)}\n\n"
                
                # Save assistant message to database
                if full_response:
                    assistant_msg = ChatMessage(
                        chat_id=chat.id,
                        role=ChatRole.ASSISTANT,
                        content=full_response
                    )
                    db.add(assistant_msg)
                    await db.commit()
                    logger.info("Assistant message saved to database")
                
            except Exception as error:
                logger.error(f"Error in streaming chat: {error}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': str(error)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )



@router.get("/history")
async def get_chat_history(
    chat_id: str | None = None,
    current_user: User | None = Depends(get_current_user_optional),
):
    async with AsyncSessionLocal() as db:
        chat = await _get_or_create_chat(db, current_user, chat_id)
        
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at)
        )
        db_messages = result.scalars().all()
        
        messages = [
            {
                "role": msg.role.value,
                "content": msg.content,
            }
            for msg in db_messages
        ]
        
        return {
            "chat_id": str(chat.id),
            "messages": messages,
        }


@router.delete("")
async def reset_chat(
    chat_id: str | None = None,
    current_user: User | None = Depends(get_current_user_optional),
):
    async with AsyncSessionLocal() as db:
        if current_user:
            # Delete user's chat
            await db.execute(
                delete(ChatSession).where(ChatSession.user_id == current_user.id)
            )
        elif chat_id:
            try:
                chat_uuid = uuid.UUID(chat_id)
                await db.execute(
                    delete(ChatSession).where(ChatSession.id == chat_uuid)
                )
            except ValueError:
                pass
        
        await db.commit()
    
    return {"status": "success", "message": "Chat history cleared"}
