import json
import logging
from typing import Any, Dict, List

import aiohttp

from rag.retrieval.chunk_retrieval import keyword_search
from rag.retrieval.document_retrieval import (
    list_documents,
    list_sections,
    read_sections,
)
from rag.retrieval.product_search import get_product, get_products, list_products
from rag.retrieval.web_search import web_search


logger = logging.getLogger(__name__)


LIST_DOCUMENTS_TOOL = {
    "type": "function",
    "function": {
        "name": "list_documents",
        "parameters": {},
    },
}
LIST_SECTIONS_TOOL = {
    "type": "function",
    "function": {
        "name": "list_sections",
        "parameters": {
            "type": "object",
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Markdown documents to extract sections from.",
                }
            },
            "required": ["documents"],
        },
    },
}
READ_SECTIONS_TOOL = {
    "type": "function",
    "function": {
        "name": "read_sections",
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of section headings to retrieve content for. The content of a section includes all its subsections.",
                },
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Markdown documents to retrieve sections from.",
                },
            },
            "required": ["sections", "documents"],
        },
    },
}
KEYWORD_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "keyword_search",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of keywords for full-text search. Keywords must be as short (no more than 4 words) and unique as possible.",
                },
                "target_documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of source documents .",
                },
            },
            "required": ["keywords"],
        },
    },
}
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on the web.",
                }
            },
            "required": ["query"],
        },
    },
}
GET_PRODUCT_TOOL = {
    "type": "function",
    "function": {
        "name": "get_product",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "The GPU name. Keep it as short as possible for the best chance of getting a match. For example, searching '4090' will match 'GeForce RTX 4090'.",
                }
            },
            "required": ["product_name"],
        },
    },
}
LIST_PRODUCTS_TOOL = {
    "type": "function",
    "function": {
        "name": "list_products",
        "parameters": {},
    },
}
GET_PRODUCTS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_products",
        "parameters": {
            "type": "object",
            "properties": {
                "product_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of product names to retrieve (e.g., ['4090', '4080'] will match 'GeForce RTX 4090' and 'GeForce RTX 4080').",
                },
                "min_price": {
                    "type": "number",
                    "description": "Minimum price filter in dollars.",
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price filter in dollars.",
                },
                "min_memory": {
                    "type": "integer",
                    "description": "Minimum memory in GB (e.g., 8, 12, 16, 24).",
                },
                "product_line": {
                    "type": "string",
                    "description": "Filter by product line. Available values: 'Consumer Desktop', 'Consumer Laptop', 'Data Center', 'Professional Desktop'.",
                },
                "architecture": {
                    "type": "string",
                    "description": "Filter by architecture. Available values: 'Blackwell', 'Ada', 'Hopper', 'Ampere', 'Turing'.",
                },
                "min_stock": {
                    "type": "integer",
                    "description": "Minimum stock quantity.",
                },
            },
        },
    },
}
TOOLS = [LIST_DOCUMENTS_TOOL, LIST_SECTIONS_TOOL, READ_SECTIONS_TOOL, KEYWORD_SEARCH_TOOL, WEB_SEARCH_TOOL, GET_PRODUCT_TOOL, LIST_PRODUCTS_TOOL, GET_PRODUCTS_TOOL]


async def _get_tool_call_result(
    function_name: str,
    function_args: dict,
    query_embedding: List[float],
    http_session: aiohttp.ClientSession,
) -> str:
    """
    Execute a single tool call and return its result.

    Args:
        function_name (str): Name of the function to call
        function_args (dict): Arguments for the function
        query_embedding (List[float]): Original user query embedding for context
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests

    Returns:
        str: The result of the tool call
    """
    if function_name == "keyword_search":
        return await keyword_search(
            query_embedding=query_embedding,
            keywords=function_args["keywords"],
            target_documents=function_args.get("target_documents"),
        )

    if function_name == "list_documents":
        return await list_documents()

    if function_name == "list_sections":
        return await list_sections(
            documents=function_args["documents"],
        )

    if function_name == "read_sections":
        return await read_sections(
            sections=function_args["sections"],
            documents=function_args["documents"],
        )
    
    if function_name == "web_search":
        return await web_search(
            query=function_args["query"],
            http_session=http_session,
        )

    if function_name == "get_product":
        return await get_product(
            product_name=function_args["product_name"],
        )

    if function_name == "list_products":
        return await list_products()

    if function_name == "get_products":
        return await get_products(
            product_names=function_args.get("product_names"),
            min_price=function_args.get("min_price"),
            max_price=function_args.get("max_price"),
            min_memory=function_args.get("min_memory"),
            product_line=function_args.get("product_line"),
            architecture=function_args.get("architecture"),
            min_stock=function_args.get("min_stock"),
        )

    raise ValueError(f"Invalid tool '{function_name}'")


async def handle_tool_calls(
    assistant_message: Dict[str, Any],
    query_embedding: List[float],
    http_session: aiohttp.ClientSession,
) -> List[Dict[str, Any]]:
    """
    Handle tool calls from the assistant's message and return results as messages.

    Args:
        assistant_message (Dict[str, Any]): The assistant's message containing tool calls
        query_embedding (List[float]): Original user query embedding for context
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests

    Returns:
        List[Dict[str, Any]]: List of tool result messages to append to the conversation
    """
    tool_messages: List[Dict[str, Any]] = []

    for tool_call in assistant_message["tool_calls"]:
        function_name = tool_call["function"]["name"]
        function_args = json.loads(tool_call["function"]["arguments"])
        logger.debug(f"Model called {function_name} with args {function_args}")

        try:
            tool_result = await _get_tool_call_result(
                function_name=function_name,
                function_args=function_args,
                query_embedding=query_embedding,
                http_session=http_session,
            )
        except Exception as error:
            logger.error(f"Error with tool '{function_name}': {error}")
            tool_result = f"Error: {str(error)}\nPlease try again."

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result,
            }
        )
        logger.debug(f"Tool '{function_name}' returned: {tool_result}")

    return tool_messages