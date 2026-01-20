"""
Utility functions for PDF to Anki flashcard generation.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any


def setup_logging(log_file: str = "outputs/processing.log", level=logging.INFO):
    """
    Configure logging to both file and console.

    Args:
        log_file: Path to log file
        level: Logging level (default: INFO)
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        ensure_dir(log_dir)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")
    return logger


def ensure_dir(path: str) -> None:
    """
    Create directory if it doesn't exist.

    Args:
        path: Directory path to create
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def save_file(path: str, content: str, encoding: str = 'utf-8') -> None:
    """
    Safely write content to a file.

    Args:
        path: File path to write to
        content: Content to write
        encoding: File encoding (default: utf-8)
    """
    # Ensure parent directory exists
    parent_dir = os.path.dirname(path)
    if parent_dir:
        ensure_dir(parent_dir)

    with open(path, 'w', encoding=encoding) as f:
        f.write(content)

    logger = logging.getLogger(__name__)
    logger.info(f"Saved file: {path}")


def generate_report(stats: Dict[str, Any]) -> str:
    """
    Generate a processing summary report.

    Args:
        stats: Dictionary with processing statistics

    Returns:
        Formatted report string
    """
    report = []
    report.append("\n" + "="*60)
    report.append("PROCESSING SUMMARY")
    report.append("="*60)

    if 'total_pdfs' in stats:
        report.append(f"Total PDFs processed: {stats['total_pdfs']}")

    if 'total_cards' in stats:
        report.append(f"Total flashcards generated: {stats['total_cards']}")

    if 'total_images' in stats:
        report.append(f"Total images extracted: {stats['total_images']}")

    if 'units' in stats:
        report.append("\nCards by unit:")
        for unit, count in stats['units'].items():
            report.append(f"  {unit}: {count} cards")

    if 'errors' in stats and stats['errors']:
        report.append(f"\nErrors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            report.append(f"  - {error}")

    if 'processing_time' in stats:
        report.append(f"\nTotal processing time: {stats['processing_time']:.2f} seconds")

    report.append("="*60)

    return "\n".join(report)


def extract_unit_number(unit_name: str) -> str:
    """
    Extract unit number from unit name.

    Args:
        unit_name: Unit name like "unit1_introduction"

    Returns:
        Unit number like "unit1" or empty string if not found
    """
    import re
    match = re.match(r'(unit\d+)', unit_name)
    return match.group(1) if match else ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re
    # Remove or replace invalid filename characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    return sanitized


def read_file(path: str, encoding: str = 'utf-8') -> str:
    """
    Safely read content from a file.

    Args:
        path: File path to read from
        encoding: File encoding (default: utf-8)

    Returns:
        File content as string
    """
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def count_lines(text: str) -> int:
    """
    Count non-empty lines in text.

    Args:
        text: Text content

    Returns:
        Number of non-empty lines
    """
    return len([line for line in text.split('\n') if line.strip()])


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
