import asyncio
import logging
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

import aiohttp

from config import (
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_LLM_API_URL,
    OPEN_ROUTER_EMBEDDING_API_URL,
    REQUEST_TIMEOUT_SECONDS,
    LLM_NAME,
    EMBEDDING_MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
    EMBEDDING_DIMENSIONS,
    MAX_ITERATIONS,
)
from rag.tool_calling import handle_tool_calls, TOOLS


logger = logging.getLogger(__name__)


class TextContent(TypedDict):
    type: Literal["text"]
    text: str


class ImageContentPart(TypedDict):
    type: Literal["image_url"]
    image_url: dict[str, str]


ContentPart = TextContent | ImageContentPart


class FunctionDescription(TypedDict, total=False):
    description: Optional[str]
    name: str
    parameters: Dict[str, Any]


class Tool(TypedDict):
    type: Literal["function"]
    function: FunctionDescription


class FunctionCall(TypedDict):
    name: str
    arguments: str


class ToolCall(TypedDict):
    id: str
    type: Literal["function"]
    function: FunctionCall


class Message(TypedDict, total=False):
    role: Literal["user", "assistant", "system", "developer", "tool"]
    content: str | List[ContentPart] | None
    name: str
    tool_calls: List[ToolCall]
    tool_call_id: str


async def embed(
    text: Union[str, List[str]],
    http_session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> Union[List[float], List[List[float]]]:
    """
    Call the OpenRouter Embedding API to get vector embeddings for text(s).

    Args:
        text (Union[str, List[str]]): A single text string or a list of text strings to be vectorized
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests

    Returns:
        Union[List[float], List[List[float]]]: 
            - If text is a string: A single embedding vector with EMBEDDING_DIMENSIONS elements
            - If text is a list of strings: A list of embedding vectors, each with EMBEDDING_DIMENSIONS elements
    """
    headers = {
        "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": EMBEDDING_MODEL_NAME,
        "input": text,
        "dimensions": EMBEDDING_DIMENSIONS,
        "encoding_format": "float"
    }
    async with semaphore:
        async with http_session.post(
            OPEN_ROUTER_EMBEDDING_API_URL,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
        ) as response:
            response.raise_for_status()
            result = await response.json()
    
    data = result["data"]
    if isinstance(text, str):
        # Single text input - return single embedding
        embedding = data[0]["embedding"]
        if len(embedding) != EMBEDDING_DIMENSIONS:
            logger.warning(
                f"Expected embedding dimension {EMBEDDING_DIMENSIONS}, but got {len(embedding)}"
            )
        return embedding

    # Multiple texts input - return list of embeddings
    embeddings = []
    for embedding_data in data:
        embedding = embedding_data["embedding"]
        if len(embedding) != EMBEDDING_DIMENSIONS:
            logger.warning(
                f"Expected embedding dimension {EMBEDDING_DIMENSIONS}, but got {len(embedding)}"
            )
        embeddings.append(embedding)
    return embeddings


async def _get_llm_response(
    messages: List[Message],
    http_session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> Message:
    """
    Call the OpenRouter API with a list of messages and return the assistant's message.

    Args:
        messages (List[Message]): The conversation messages
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests

    Returns:
        Message: The assistant's message object
    """
    headers = {
        "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "tool_choice": "auto",
    }
    if TOOLS:
        payload["tools"] = TOOLS

    async with semaphore:
        async with http_session.post(
            OPEN_ROUTER_LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return result["choices"][0]["message"]


async def get_llm_response(
    messages: List[Message],
    query_embedding: List[float],
    http_session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> List[Message]:
    """
    Call the LLM API to get a response for a given prompt.

    Args:
        messages (List[Message]): The conversation messages
        query_embedding (List[float]): Query embedding for semantic search
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests

    Returns:
        List[Message]: The entire conversation messages array
    """

    for _ in range(1, MAX_ITERATIONS + 1):
        assistant_message = await _get_llm_response(
            messages=messages,
            http_session=http_session,
            semaphore=semaphore,
        )
        messages.append(assistant_message)
        if assistant_message.get("tool_calls"):
            # Handle tool calls
            tool_messages = await handle_tool_calls(
                assistant_message=assistant_message,
                query_embedding=query_embedding,
            )
            messages.extend(tool_messages)
            continue
