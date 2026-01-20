"""
Image extraction and path resolution for Anki cards.

Extracts image references from HTML content and resolves paths for genanki packaging.
"""

import re
import logging
from pathlib import Path
from typing import List, Tuple


logger = logging.getLogger(__name__)


def extract_image_references(card_html: str) -> List[str]:
    """
    Find all <img src="..."> tags in HTML and extract filenames.

    Args:
        card_html: HTML content of a card

    Returns:
        List of image paths found in the HTML
    """
    # Pattern to match <img src="..."> tags
    pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'

    matches = re.findall(pattern, card_html, re.IGNORECASE)

    return matches


def resolve_image_path(relative_path: str, images_dir: str) -> str:
    """
    Convert relative path to absolute path.

    Args:
        relative_path: Relative path from card (e.g., "../images/file.png")
        images_dir: Absolute path to images directory

    Returns:
        Absolute path to image file
    """
    images_dir = Path(images_dir)

    # Extract just the filename (in case it's a path)
    # Handles both "../images/file.png" and "file.png"
    if '/' in relative_path:
        filename = Path(relative_path).name
    else:
        filename = relative_path

    # Construct absolute path
    absolute_path = images_dir / filename

    return str(absolute_path)


def prepare_card_for_apkg(card_html: str, images_dir: str) -> Tuple[str, List[str]]:
    """
    Prepare card HTML for .apkg export by:
    1. Finding all image references
    2. Resolving them to absolute paths
    3. Replacing src attributes with just filenames

    Args:
        card_html: Original HTML content with relative image paths
        images_dir: Path to images directory

    Returns:
        Tuple of:
        - Modified HTML with just filenames in src attributes
        - List of absolute paths to all referenced images
    """
    # Find all image references
    image_refs = extract_image_references(card_html)

    if not image_refs:
        # No images, return as-is
        return card_html, []

    # Track absolute paths for genanki media
    absolute_paths = []

    # Track which images we've already processed (avoid duplicates)
    seen_images = set()

    # Process each image reference
    modified_html = card_html

    for img_path in image_refs:
        # Extract filename
        if '/' in img_path:
            filename = Path(img_path).name
        else:
            filename = img_path

        # Resolve to absolute path
        absolute_path = resolve_image_path(img_path, images_dir)

        # Check if file exists
        if not Path(absolute_path).exists():
            logger.warning(f"Image file not found: {absolute_path}")
        else:
            # Add to media list (only once per unique file)
            if filename not in seen_images:
                absolute_paths.append(absolute_path)
                seen_images.add(filename)

        # Replace the path in HTML with just the filename
        # This handles the full <img src="..."> tag
        modified_html = modified_html.replace(
            f'src="{img_path}"',
            f'src="{filename}"'
        )
        modified_html = modified_html.replace(
            f"src='{img_path}'",
            f'src="{filename}"'
        )

    logger.debug(f"Processed {len(image_refs)} image references, {len(absolute_paths)} unique files")

    return modified_html, absolute_paths


def get_all_images_for_deck(cards: List[dict], images_dir: str) -> List[str]:
    """
    Get all unique image files referenced across all cards in a deck.

    Args:
        cards: List of card dictionaries with 'front' and 'back' fields
        images_dir: Path to images directory

    Returns:
        List of absolute paths to all unique images
    """
    all_images = set()

    for card in cards:
        # Process front
        _, front_images = prepare_card_for_apkg(card['front'], images_dir)
        all_images.update(front_images)

        # Process back
        _, back_images = prepare_card_for_apkg(card['back'], images_dir)
        all_images.update(back_images)

    return list(all_images)
