"""
LLM Map-Reduce module.
Splits HTML content into manageable chunks and uses the LLM client to summarize each chunk.
"""

import re
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)

def clean_html(html_content):
    """
    Uses BeautifulSoup to strip HTML tags and returns plain text.
    """
    soup = BeautifulSoup(html_content, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator="\n")
    return text

def split_text(text, max_tokens=800):
    """
    Recursively splits text into chunks of roughly max_tokens tokens.
    For simplicity, tokens are approximated by words.
    Increased to 800 to reduce number of LLM calls and avoid rate limits.
    """
    words = text.split()
    if len(words) <= max_tokens:
        return [text]
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def summarize_chunk(chunk, llm_client):
    """
    Uses the LLM client to summarize a chunk.
    """
    prompt = f"Summarize the following text in a concise manner:\n\n{chunk}\n\nSummary:"
    summary = llm_client.call_llm(prompt)
    return summary.strip()

def map_reduce(html_content, llm_client):
    """
    Performs the map-reduce:
      1. Clean HTML to text.
      2. Split text into chunks.
      3. Summarize each chunk (with rate limiting).
      4. Concatenate summaries.
    """
    logger.info("Starting map-reduce summarization.")
    text = clean_html(html_content)

    # Skip if content is empty or too small
    if not text or len(text.strip()) < 50:
        logger.debug("Content too small or empty, skipping summarization")
        return ""

    chunks = split_text(text)
    logger.debug("Split content into %d chunks", len(chunks))

    summaries = []
    for i, chunk in enumerate(chunks):
        logger.debug("Summarizing chunk %d/%d", i+1, len(chunks))
        summary = summarize_chunk(chunk, llm_client)
        summaries.append(summary)

    final_summary = "\n".join(summaries)
    return final_summary