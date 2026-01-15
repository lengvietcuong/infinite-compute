"""
Module for retrieving knowledge chunks from the database using semantic and keyword search.
"""

import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy import select, or_, func, and_

from config import SEMANTIC_SEARCH_TOP_K, SEMANTIC_SEARCH_SIMILARITY_THRESHOLD, KEYWORD_SEARCH_TOP_K
from database.database import AsyncSessionLocal
from database.models import DocumentChunk


logger = logging.getLogger(__name__)


@dataclass
class KnowledgeChunk:
    """Represents a retrieved knowledge chunk."""

    content: str
    source_file: str
    similarity: float


async def semantic_search(
    query_embedding: List[float],
    top_k: int = SEMANTIC_SEARCH_TOP_K,
    similarity_threshold: float = SEMANTIC_SEARCH_SIMILARITY_THRESHOLD,
) -> str | None:
    """
    Retrieve relevant knowledge from the database using semantic search.

    Args:
        query_embedding (List[float]): Query embedding vector
        http_session (aiohttp.ClientSession): aiohttp session for API requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests
        top_k (int): Number of top results to retrieve (default from config)
        similarity_threshold (float): Minimum similarity score to include (default from config)

    Returns:
        str | None: Formatted string with retrieved knowledge chunks
    """
    logger.debug(f"Performing semantic search")

    distance = DocumentChunk.embedding.cosine_distance(query_embedding).label(
        "distance"
    )
    similarity = (1 - distance).label("similarity")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                DocumentChunk.content,
                DocumentChunk.source_file,
                similarity,
            )
            .where(similarity >= similarity_threshold)
            .order_by(similarity.desc())
            .limit(top_k)
        )
        rows = result.fetchall()

    if not rows:
        logger.debug("No semantic search results found.")
        return None

    chunks = []
    for row in rows:
        chunk = KnowledgeChunk(
            content=row[0],
            source_file=row[1],
            similarity=row[2],
        )
        chunks.append(chunk)
        logger.debug(
            f"Selected chunk: content={chunk.content[:50]}..., source={chunk.source_file}, similarity={chunk.similarity:.4f}"
        )
    formatted_result = _format_knowledge_chunks(chunks)
    logger.debug(f"Semantic search found {len(chunks)} chunks")

    return formatted_result


async def keyword_search(
    query_embedding: List[float],
    keywords: List[str],
    top_k: int = KEYWORD_SEARCH_TOP_K,
    target_documents: List[str] | None = None,
) -> str | None:
    """
    Perform full-text search, retrieve top results based on cosine similarity, rerank them, and return the most relevant chunks.

    Args:
        query_embedding (List[float]): Query embedding vector
        keywords (List[str]): List of unique keywords for full-text search
        http_session (aiohttp.ClientSession): aiohttp session for API requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests
        top_k (int): Number of top results to return after reranking (default from config)
        target_documents (List[str] | None): Optional list of target source files to filter results. If None, search all files.

    Returns:
        str | None: Formatted string with retrieved knowledge chunks
    """
    logger.debug(f"Performing keyword search for {keywords}")

    distance = DocumentChunk.embedding.cosine_distance(query_embedding).label(
        "distance"
    )
    similarity = (1 - distance).label("similarity")

    conditions = [
        func.lower(DocumentChunk.content).contains(keyword.lower())
        for keyword in keywords
    ]
    where_conditions = [or_(*conditions)]
    if target_documents is not None:
        where_conditions.append(DocumentChunk.source_file.in_(target_documents))

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                DocumentChunk.content,
                DocumentChunk.source_file,
                similarity,
            )
            .where(and_(*where_conditions))
            .order_by(similarity.desc())
            .limit(top_k)
        )
        rows = result.fetchall()

    if not rows:
        logger.debug(f"No chunks found for keywords {keywords}.")
        return None

    chunks = []
    for row in rows:
        chunk = KnowledgeChunk(
            content=row[0],
            source_file=row[1],
            similarity=row[2],
        )
        chunks.append(chunk)
        logger.debug(
            f"Selected chunk: content={chunk.content[:50]}..., source={chunk.source_file}, similarity={chunk.similarity:.4f}"
        )

    formatted_result = _format_knowledge_chunks(chunks)
    logger.debug(f"Keyword search found {len(chunks)} chunks for keywords: {keywords}")

    return formatted_result


def _format_knowledge_chunks(chunks: List[KnowledgeChunk]) -> str:
    """
    Format knowledge chunks for LLM consumption.

    Args:
        chunks (List[KnowledgeChunk]): List of retrieved knowledge chunks

    Returns:
        str: Formatted string with all chunks
    """
    formatted_parts = []
    for chunk in chunks:
        formatted_parts.append(f"{chunk.source_file}:\n")
        formatted_parts.append(f"  {chunk.content}")

    return "\n".join(formatted_parts)
