"""
TSV parser for Anki .txt files.

Parses tab-separated Anki deck files with headers and extracts card data.
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
from src.config import Config


logger = logging.getLogger(__name__)


def parse_anki_tsv(file_path: str, config: Optional[Config] = None) -> Dict[str, any]:
    """
    Parse an Anki .txt file in TSV format.

    Args:
        file_path: Path to the .txt file
        config: Optional Config instance for subject-specific deck naming

    Returns:
        Dictionary with:
        - 'deck_name': str - Deck name from header or default
        - 'cards': list[dict] - List of card dicts with 'front', 'back', 'tags'

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if config is None:
        config = Config()

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Parse headers and extract deck name
    deck_name = None
    header_end = 0

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines at the start
        if not line:
            continue

        # Parse headers
        if line.startswith('#'):
            if line.startswith('#deck:'):
                deck_name = line[6:].strip()
            header_end = i + 1
        # First non-header, non-empty line should be column headers
        elif 'Front' in line and 'Back' in line and 'Tags' in line:
            header_end = i + 1
            break
        else:
            # Found content before column headers
            break

    # Default deck name if not found
    if deck_name is None:
        # Extract from filename (e.g., "unit3_bayesian_networks_anki.txt" -> "Unit 3: Bayesian Networks")
        unit_name = file_path.stem.replace('_anki', '').replace('_', ' ').title()
        subject_short = config.subject_short_name
        deck_name = f"{subject_short} - {unit_name}"

    # Parse cards
    cards = []

    for i in range(header_end, len(lines)):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            continue

        # Skip comment lines
        if line.startswith('#'):
            continue

        # Split by tab
        parts = line.split('\t')

        # Validate 3 columns
        if len(parts) != 3:
            logger.warning(f"Skipping line {i+1}: Expected 3 columns, got {len(parts)}")
            continue

        front, back, tags_str = parts

        # Parse tags (space-separated)
        tags = tags_str.strip().split() if tags_str.strip() else []

        cards.append({
            'front': front.strip(),
            'back': back.strip(),
            'tags': tags
        })

    logger.info(f"Parsed {len(cards)} cards from {file_path.name}")

    return {
        'deck_name': deck_name,
        'cards': cards
    }


def validate_card(card: Dict[str, any]) -> bool:
    """
    Validate a card has required fields.

    Args:
        card: Card dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ['front', 'back', 'tags']

    for field in required_fields:
        if field not in card:
            logger.warning(f"Card missing required field: {field}")
            return False

    # Check non-empty front and back
    if not card['front'] or not card['back']:
        logger.warning("Card has empty front or back")
        return False

    return True
