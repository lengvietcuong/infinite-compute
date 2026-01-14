"""
Document-level retrieval functions for listing and reading document topics, documents, and sections.
"""

import logging
from collections import defaultdict
from typing import List, Set

import mistune
from mistune.core import BlockState
from mistune.renderers.markdown import MarkdownRenderer
from mistune.toc import add_toc_hook
from sqlalchemy import select

from config import MAX_HEADING_DEPTH
from database.database import AsyncSessionLocal
from database.models import Document


logger = logging.getLogger(__name__)


async def list_documents(topics: List[str]) -> str:
    """
    List all documents from the database filtered by topics.

    Args:
        topics (List[str]): List of topics to filter by

    Returns:
        str: Formatted string with documents organized by topic
    """
    logger.debug(f"Listing documents for topics: {topics}")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document.topic, Document.source_file)
            .where(Document.topic.in_(topics))
            .order_by(Document.topic, Document.source_file)
        )
        rows = result.fetchall()

    if not rows:
        raise ValueError("Invalid topic(s).")

    # Group documents by topic
    topic_documents = defaultdict(list)
    for topic, source_file in rows:
        topic_documents[topic].append(source_file)

    # Format output
    formatted_parts = []
    for topic in topics:
        if topic not in topic_documents:
            continue
        formatted_parts.append(f"{topic}:")
        for doc in topic_documents[topic]:
            formatted_parts.append(f"- {doc}")
        formatted_parts.append("")

    result_str = "\n".join(formatted_parts).strip()
    logger.debug(
        f"Listed {len(rows)} documents for {len(topics)} topics:\n{result_str}"
    )
    return result_str


async def list_sections(
    documents: List[str], max_heading_depth: int = MAX_HEADING_DEPTH
) -> str:
    """
    List all headings of each document using the Markdown parser.

    Args:
        documents (List[str]): List of document file paths to parse
        max_heading_depth (int): Maximum heading depth to include

    Returns:
        str: Formatted string with document headings organized hierarchically
    """
    logger.debug(f"Listing sections for {len(documents)} documents")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document.source_file, Document.content).where(
                Document.source_file.in_(documents)
            )
        )
        rows = result.fetchall()

    if not rows:
        raise ValueError("Invalid document(s).")

    # Extract Table of Contents (TOC)
    markdown = mistune.create_markdown()
    add_toc_hook(markdown, min_level=1, max_level=max_heading_depth)
    formatted_parts = []

    for source_file, content in rows:
        _, state = markdown.parse(content)
        toc_items = state.env.get("toc_items", [])
        if not toc_items:
            continue

        formatted_parts.append(f"{source_file}:")
        for level, _, text in toc_items:
            indent = "  " * (level - 1)
            heading_marker = "#" * level
            formatted_parts.append(f"{indent}{heading_marker} {text}")
        formatted_parts.append("")

    result_str = "\n".join(formatted_parts).strip()
    logger.debug(
        f"Listed {len(formatted_parts)} sections for {len(documents)} documents:\n{result_str}"
    )
    return result_str


def clean_heading(heading: str) -> str:
    """
    Remove heading markers (hashtags) and formatting from a string and normalize.

    Args:
        heading (str): Text that may contain heading markers and formatting (e.g., "## **Heading**")

    Returns:
        str: Normalized text with markers and formatting removed (lowercase, stripped)
    """
    stripped = heading.strip()
    stripped = stripped.lstrip("#").strip()
    stripped = stripped.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
    return stripped.lower()


async def read_sections(sections: List[str], documents: List[str]) -> str:
    """
    Read the contents of specific sections from provided documents.
    When a heading is selected, its content and all subheadings are included.

    Args:
        sections (List[str]): List of section headings to retrieve
        documents (List[str]): List of document file paths to search

    Returns:
        str: Formatted string with section contents organized by document
    """
    logger.debug(f"Reading {len(sections)} sections from {len(documents)} documents")

    markdown = mistune.create_markdown(renderer=None)
    renderer = MarkdownRenderer()
    state = BlockState()
    target_sections = {clean_heading(section) for section in sections}

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document.source_file, Document.content).where(
                Document.source_file.in_(documents)
            )
        )
        rows = result.fetchall()

    if not rows:
        raise ValueError("Invalid document(s).")

    formatted_parts = []
    for source_file, content in rows:
        tokens = markdown(content)
        extracted_sections = _extract_matching_sections(
            tokens, target_sections, renderer, state
        )

        if extracted_sections:
            formatted_parts.append(f"{source_file}:")
            formatted_parts.extend(extracted_sections)
            formatted_parts.append("")

    if not formatted_parts:
        raise ValueError("Invalid section(s).")

    result_str = "\n".join(formatted_parts).strip()
    logger.debug(
        f"Read {len(sections)} sections from {len(documents)} documents:\n{result_str}"
    )
    return result_str


def _extract_matching_sections(
    tokens: List[dict],
    target_sections: Set[str],
    renderer: MarkdownRenderer,
    state: BlockState,
) -> List[str]:
    """Extract sections matching target headings from token list.

    Args:
        tokens (List[dict]): List of parsed markdown tokens
        target_sections (Set[str]): Set of target section headings (lowercase)
        renderer (MarkdownRenderer): Markdown renderer instance
        state (BlockState): Block state for rendering

    Returns:
        List[str]: List of extracted section contents as markdown strings
    """
    extracted_sections = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        # Check is heading
        if token.get("type") != "heading":
            i += 1
            continue

        # Check has text inside
        heading_children = token.get("children", [])
        if not heading_children or heading_children[0].get("type") != "text":
            i += 1
            continue

        # Check is target section
        heading_text = heading_children[0].get("raw", "").strip()
        if clean_heading(heading_text) not in target_sections:
            i += 1
            continue

        heading_level = token.get("attrs", {}).get("level", 1)
        section_tokens = [token]
        i += 1
        # Collect all tokens until next same-or-higher level heading
        while i < len(tokens):
            next_token = tokens[i]
            if (
                next_token.get("type") == "heading"
                and next_token.get("attrs", {}).get("level", 1) <= heading_level
            ):
                break
            section_tokens.append(next_token)
            i += 1

        section_markdown = renderer(section_tokens, state=state)
        extracted_sections.append(section_markdown.strip())

    return extracted_sections
