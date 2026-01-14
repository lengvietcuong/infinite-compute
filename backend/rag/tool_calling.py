import json
import logging
from typing import Any, Dict, List

from rag.chunk_retrieval import keyword_search
from rag.document_retrieval import (
    list_documents,
    list_sections,
    read_sections,
)


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
TOOLS = [LIST_DOCUMENTS_TOOL, LIST_SECTIONS_TOOL, READ_SECTIONS_TOOL, KEYWORD_SEARCH_TOOL]


async def _get_tool_call_result(
    function_name: str,
    function_args: dict,
    query_embedding: List[float]
) -> str:
    """
    Execute a single tool call and return its result.

    Args:
        function_name (str): Name of the function to call
        function_args (dict): Arguments for the function
        query (List[float]): Original user query embedding for context
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests

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

    raise ValueError(f"Invalid tool '{function_name}'")


async def handle_tool_calls(
    assistant_message: Dict[str, Any],
    query_embedding: List[float],
) -> List[Dict[str, Any]]:
    """
    Handle tool calls from the assistant's message and return results as messages.

    Args:
        assistant_message (Message): The assistant's message containing tool calls
        query_embedding (List[float]): Original user query embedding for context

    Returns:
        List[Message]: List of tool result messages to append to the conversation
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
                query_embedding=query_embedding
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