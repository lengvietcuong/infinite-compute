"""Module for performing web searches using the Brave Search API."""

import aiohttp

from config import BRAVE_API_KEY, BRAVE_API_URL, REQUEST_TIMEOUT_SECONDS


async def web_search(query: str, http_session: aiohttp.ClientSession) -> str:
    """
    Perform a web search using the Brave Search API.

    Args:
        query (str): The search query
        http_session (aiohttp.ClientSession): aiohttp ClientSession for making HTTP requests

    Returns:
        str: Formatted search results
    """
    if not BRAVE_API_KEY:
        raise ValueError("Web search is not available (API key not configured)")

    params = {"q": query}
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }

    async with http_session.get(
        BRAVE_API_URL,
        params=params,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
    ) as response:
        response.raise_for_status()
        data = await response.json()

    results = []
    web_results = data.get("web", {}).get("results", [])
    
    for idx, result in enumerate(web_results[:5], 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        description = result.get("description", "No description")
        results.append(f"{idx}. {title}\n   URL: {url}\n   {description}")

    if not results:
        raise ValueError("No web search results found.")

    return "\n\n".join(results)