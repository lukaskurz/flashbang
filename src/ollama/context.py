"""
Utility for extracting page context from markdown files to enhance image descriptions.
"""

import re
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def extract_page_text(unit_name: str, page_number: int, max_chars: int = 500) -> Optional[str]:
    """
    Extract text content from a specific page in the markdown file.

    Args:
        unit_name: Unit name (e.g., 'unit3_bayesian_networks')
        page_number: Page number to extract
        max_chars: Maximum characters to return (default 500)

    Returns:
        Page text content, truncated if needed, or None if page not found

    Raises:
        FileNotFoundError: If markdown file doesn't exist
    """
    # Construct markdown file path
    markdown_dir = Path(__file__).parent.parent.parent / "outputs" / "markdown"
    markdown_path = markdown_dir / f"{unit_name}.md"

    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    # Read the markdown file
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the page section using regex
    # Pattern: ## Page {page_number} ... until next ## Page or end of file
    pattern = rf"## Page {page_number}\n(.*?)(?=\n## Page \d+|$)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        logger.warning(f"Page {page_number} not found in {unit_name}")
        return None

    page_text = match.group(1)

    # Clean the text
    cleaned_text = _clean_page_text(page_text, max_chars)

    return cleaned_text


def _clean_page_text(text: str, max_chars: int) -> str:
    """
    Clean extracted page text by removing images, extra whitespace, etc.

    Args:
        text: Raw page text
        max_chars: Maximum characters to return

    Returns:
        Cleaned text
    """
    # Remove "Available Images" sections and image references
    text = re.sub(r'### Available Images.*?(?=\n##|\Z)', '', text, flags=re.DOTALL)

    # Remove markdown image syntax: ![filename](path)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Remove extra whitespace and newlines
    text = re.sub(r'\n{3,}', '\n\n', text)  # Replace 3+ newlines with 2
    text = re.sub(r' +', ' ', text)  # Replace multiple spaces with single space
    text = text.strip()

    # Truncate if needed
    if len(text) > max_chars:
        # Try to truncate at sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')

        # Use the last sentence or paragraph boundary if within reasonable distance
        boundary = max(last_period, last_newline)
        if boundary > max_chars * 0.7:  # If boundary is in last 30%, use it
            text = text[:boundary + 1]
        else:
            text = truncated + '...'

    return text
