import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional, TypedDict, Union

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
                http_session=http_session,
            )
            messages.extend(tool_messages)
            continue
        
        # No tool calls, conversation is complete
        break

    return messages


async def stream_llm_response(
    messages: List[Message],
    query_embedding: List[float],
    http_session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream LLM responses with support for tool calling.
    
    Yields events in the following format:
    - {"type": "content", "content": str} - Text content delta
    - {"type": "tool_call_start", "tool_name": str} - Tool call started
    - {"type": "tool_call_end", "tool_name": str, "result": str} - Tool call completed
    - {"type": "done", "full_content": str} - Streaming complete
    - {"type": "error", "error": str} - Error occurred

    Args:
        messages (List[Message]): The conversation messages
        query_embedding (List[float]): Query embedding for semantic search
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests

    Yields:
        Dict[str, Any]: Event objects representing streaming events
    """
    
    iteration = 0
    for iteration in range(1, MAX_ITERATIONS + 1):
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
            "stream": True,
        }
        if TOOLS:
            payload["tools"] = TOOLS

        full_content = ""
        tool_calls_dict: Dict[int, ToolCall] = {}
        
        try:
            async with semaphore:
                async with http_session.post(
                    OPEN_ROUTER_LLM_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        
                        if not line or line.startswith(':'):
                            continue
                        
                        if line.startswith('data: '):
                            data_str = line[6:]
                            
                            if data_str == '[DONE]':
                                break
                            
                            try:
                                chunk = json.loads(data_str)
                            except json.JSONDecodeError:
                                continue
                            
                            if 'error' in chunk:
                                yield {
                                    "type": "error",
                                    "error": chunk['error'].get('message', 'Unknown error')
                                }
                                return
                            
                            choices = chunk.get('choices', [])
                            if not choices:
                                continue
                            
                            delta = choices[0].get('delta', {})
                            finish_reason = choices[0].get('finish_reason')
                            
                            # Handle content delta
                            if 'content' in delta and delta['content']:
                                content_delta = delta['content']
                                full_content += content_delta
                                yield {
                                    "type": "content",
                                    "content": content_delta
                                }
                            
                            # Handle tool calls delta
                            if 'tool_calls' in delta:
                                for tool_call_delta in delta['tool_calls']:
                                    index = tool_call_delta.get('index', 0)
                                    
                                    if index not in tool_calls_dict:
                                        tool_calls_dict[index] = {
                                            'id': tool_call_delta.get('id', ''),
                                            'type': 'function',
                                            'function': {
                                                'name': tool_call_delta.get('function', {}).get('name', ''),
                                                'arguments': ''
                                            }
                                        }
                                        
                                        if tool_calls_dict[index]['function']['name']:
                                            yield {
                                                "type": "tool_call_start",
                                                "tool_name": tool_calls_dict[index]['function']['name']
                                            }
                                    
                                    if 'function' in tool_call_delta:
                                        function_delta = tool_call_delta['function']
                                        if 'name' in function_delta:
                                            tool_calls_dict[index]['function']['name'] = function_delta['name']
                                        if 'arguments' in function_delta:
                                            tool_calls_dict[index]['function']['arguments'] += function_delta['arguments']
                                    
                                    if 'id' in tool_call_delta:
                                        tool_calls_dict[index]['id'] = tool_call_delta['id']
                            
                            # Check if streaming is complete
                            if finish_reason:
                                break
            
            # If we have tool calls, execute them
            if tool_calls_dict:
                tool_calls_list = [tool_calls_dict[i] for i in sorted(tool_calls_dict.keys())]
                
                assistant_message: Message = {
                    "role": "assistant",
                    "content": full_content or None,
                    "tool_calls": tool_calls_list
                }
                messages.append(assistant_message)
                
                # Execute tool calls
                tool_messages = await handle_tool_calls(
                    assistant_message=assistant_message,
                    query_embedding=query_embedding,
                    http_session=http_session,
                )
                messages.extend(tool_messages)
                
                # Notify about tool execution
                for tool_call in tool_calls_list:
                    yield {
                        "type": "tool_call_end",
                        "tool_name": tool_call['function']['name']
                    }
                
                # Continue to next iteration to get final response
                continue
            
            # No tool calls, streaming is complete
            assistant_message: Message = {
                "role": "assistant",
                "content": full_content
            }
            messages.append(assistant_message)
            
            yield {
                "type": "done",
                "full_content": full_content
            }
            break
            
        except Exception as error:
            logger.error(f"Error during streaming: {error}")
            yield {
                "type": "error",
                "error": str(error)
            }
            return
    
    # If we exit the loop without breaking, we've hit max iterations
    if iteration >= MAX_ITERATIONS:
        logger.warning("Max iterations reached during streaming")

