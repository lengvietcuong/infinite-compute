"""
Knowledge base initialization for RAG system.
Functions for loading Markdown documents, chunking, embedding, and inserting into database.
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import List

import aiohttp
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Document, DocumentChunk
from rag.inference import embed


logger = logging.getLogger(__name__)

MARKDOWN_HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
    ("#####", "h5"),
    ("######", "h6"),
]
MARKDOWN_CHUNK_SIZE = 1024
MARKDOWN_CHUNK_OVERLAP = 100
MINIMUM_CHUNK_CHARACTERS = 100


def _chunk_markdown_text(
    markdown_text: str,
    chunk_size: int = MARKDOWN_CHUNK_SIZE,
    chunk_overlap: int = MARKDOWN_CHUNK_OVERLAP,
) -> List[str]:
    """Perform hierarchical Markdown-aware chunking with full header preservation."""
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=MARKDOWN_HEADERS_TO_SPLIT_ON,
        return_each_line=False,
        strip_headers=True,
    )
    header_documents = splitter.split_text(markdown_text)

    character_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=["\n\n", "\n", ". ", "!", "?", " ", ""],
    )

    chunks: List[str] = []

    for document in header_documents:
        content = getattr(document, "page_content", str(document)).strip()
        metadata = getattr(document, "metadata", {}) or {}

        if not content:
            continue

        header_lines = []
        for level in range(1, 7):
            key = f"h{level}"
            if metadata.get(key):
                header_lines.append("#" * level + " " + metadata[key].strip())

        header_prefix = "\n".join(header_lines)

        for sub_text in character_splitter.split_text(content):
            text = sub_text.strip()
            if len(text) < MINIMUM_CHUNK_CHARACTERS:
                continue

            full_text = f"{header_prefix}\n{text}" if header_prefix else text
            chunks.append(full_text)

    return chunks


def _extract_document_topic(markdown_text: str) -> str:
    """Extract the first heading from markdown as the document topic."""
    for line in markdown_text.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            topic = line.lstrip('#').strip()
            return topic if topic else 'Untitled'
    return 'Untitled'


async def add_markdown_documents(data_directory: Path) -> None:
    """Load all Markdown documents into the documents table."""
    async with AsyncSessionLocal() as session:
        # Fetch existing documents and hashes
        result = await session.execute(
            select(Document.source_file, Document.sha256_hash)
        )
        rows = result.fetchall()

        existing_sources = {row[0] for row in rows}
        existing_hashes = {row[1] for row in rows}

        documents_to_add = []
        for markdown_file in data_directory.glob("*.md"):
            source_file = markdown_file.name
            if source_file in existing_sources:
                continue

            content = markdown_file.read_text(encoding="utf-8")
            document_hash = hashlib.sha256(content.encode("utf-8")).digest()
            if document_hash in existing_hashes:
                continue

            existing_sources.add(source_file)
            existing_hashes.add(document_hash)
            topic = _extract_document_topic(content)
            documents_to_add.append(
                Document(content=content, topic=topic, source_file=source_file)
            )

        logger.info(f"Found {len(documents_to_add)} Markdown documents to add")

        if documents_to_add:
            session.add_all(documents_to_add)
            await session.commit()


async def add_markdown_document_chunks(
    data_directory: Path,
    http_session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> None:
    """Chunk all Markdown documents and add chunks to the document_chunks table."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DocumentChunk.sha256_hash))
        existing_chunk_hashes = {row[0] for row in result.fetchall()}

        chunks_to_add = []
        for md_file in data_directory.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            chunks = _chunk_markdown_text(content)

            for i, chunk in enumerate(chunks):
                chunk_hash = hashlib.sha256(chunk.encode("utf-8")).digest()
                if chunk_hash in existing_chunk_hashes:
                    continue

                existing_chunk_hashes.add(chunk_hash)
                chunks_to_add.append((chunk, md_file.name, i))

        logger.info(f"Found {len(chunks_to_add)} Markdown chunks to add")

        if not chunks_to_add:
            return

        chunk_contents = [chunk for chunk, _, _ in chunks_to_add]
        embeddings = await embed(chunk_contents, http_session, semaphore)

        document_chunks = [
            DocumentChunk(
                content=chunk,
                embedding=embedding,
                source_file=source_file,
                chunk_index=index,
            )
            for (chunk, source_file, index), embedding in zip(chunks_to_add, embeddings)
        ]
        session.add_all(document_chunks)
        await session.commit()
