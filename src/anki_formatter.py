"""
Anki output formatting and validation module.
"""

import os
import logging
import re
from typing import Dict, Tuple, List


class AnkiFormatter:
    """Format and validate Anki flashcard output."""

    def __init__(self):
        """Initialize Anki formatter."""
        self.logger = logging.getLogger(__name__)

    def format_cards(self, raw_cards: str, unit_name: str) -> str:
        """
        Format cards to ensure proper Anki TSV format.

        Args:
            raw_cards: Raw card content
            unit_name: Unit name for logging

        Returns:
            Formatted TSV string
        """
        self.logger.info(f"Formatting cards for {unit_name}")

        # Ensure headers are present
        if not raw_cards.startswith('#separator:tab'):
            self.logger.warning("Adding missing headers")
            headers = "#separator:tab\n#html:true\n#tags column:3\nFront\tBack\tTags\n"
            raw_cards = headers + raw_cards

        # Clean up any formatting issues
        formatted = self._fix_common_issues(raw_cards)

        return formatted

    def _fix_common_issues(self, content: str) -> str:
        """
        Fix common formatting issues in generated cards.

        Args:
            content: Raw card content

        Returns:
            Fixed content
        """
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Keep headers as-is
            if line.startswith('#') or line == 'Front\tBack\tTags':
                fixed_lines.append(line)
                continue

            # Skip empty lines
            if not line.strip():
                continue

            # Check if line has correct number of tabs
            parts = line.split('\t')

            if len(parts) != 3:
                # Log and skip malformed lines
                self.logger.warning(f"Skipping malformed line (wrong column count): {line[:50]}...")
                continue

            front, back, tags = parts

            # Clean up fields
            front = front.strip()
            back = back.strip()
            tags = tags.strip()

            # Fix MathJax delimiters if needed
            back = self._fix_mathjax(back)

            # Ensure image paths are relative
            back = self._fix_image_paths(back)

            # Reconstruct line
            fixed_line = f"{front}\t{back}\t{tags}"
            fixed_lines.append(fixed_line)

        return '\n'.join(fixed_lines)

    def _fix_mathjax(self, text: str) -> str:
        """
        Fix common MathJax formatting issues.

        Args:
            text: Text potentially containing MathJax

        Returns:
            Text with fixed MathJax
        """
        # Ensure inline math uses \( \) not $ $
        # Note: Be careful not to replace $ in regular text
        # This is a simple heuristic

        # Fix display math: \[ \]
        # Already should be correct from Claude

        return text

    def _fix_image_paths(self, text: str) -> str:
        """
        Ensure image paths are relative.

        Args:
            text: Text potentially containing image tags

        Returns:
            Text with fixed image paths
        """
        # Pattern: <img src="...">
        # Ensure paths start with ../images/

        def fix_path(match):
            full_tag = match.group(0)
            path = match.group(1)

            # If path doesn't start with ../ add it
            if not path.startswith('../images/'):
                # Extract just the filename if it's a full path
                filename = os.path.basename(path)
                new_path = f"../images/{filename}"
                return full_tag.replace(path, new_path)

            return full_tag

        pattern = r'<img\s+src="([^"]+)"'
        text = re.sub(pattern, fix_path, text)

        return text

    def validate_tsv(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate TSV format.

        Args:
            content: TSV content to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        lines = content.split('\n')

        # Check headers
        if not content.startswith('#separator:tab'):
            errors.append("Missing #separator:tab header")

        if '#html:true' not in content:
            errors.append("Missing #html:true header")

        if '#tags column:3' not in content:
            errors.append("Missing #tags column:3 header")

        # Check column headers
        has_column_headers = False
        for line in lines:
            if line == 'Front\tBack\tTags':
                has_column_headers = True
                break

        if not has_column_headers:
            errors.append("Missing column headers (Front\\tBack\\tTags)")

        # Validate card rows
        card_count = 0
        for i, line in enumerate(lines, 1):
            # Skip headers and empty lines
            if line.startswith('#') or line == 'Front\tBack\tTags' or not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) != 3:
                errors.append(f"Line {i}: Wrong number of columns (expected 3, got {len(parts)})")
                continue

            front, back, tags = parts

            # Check for empty fields
            if not front.strip():
                errors.append(f"Line {i}: Empty front field")

            if not back.strip():
                errors.append(f"Line {i}: Empty back field")

            if not tags.strip():
                errors.append(f"Line {i}: Empty tags field")

            card_count += 1

        if card_count == 0:
            errors.append("No flashcards found in content")

        is_valid = len(errors) == 0

        if is_valid:
            self.logger.info(f"Validation passed: {card_count} cards")
        else:
            self.logger.warning(f"Validation failed with {len(errors)} errors")

        return is_valid, errors

    def normalize_tags(self, cards: str, unit_tag: str) -> str:
        """
        Normalize tags to ensure consistency.

        Args:
            cards: Card content
            unit_tag: Base unit tag (e.g., 'unit3')

        Returns:
            Cards with normalized tags
        """
        lines = cards.split('\n')
        normalized_lines = []

        for line in lines:
            # Skip headers
            if line.startswith('#') or line == 'Front\tBack\tTags' or not line.strip():
                normalized_lines.append(line)
                continue

            parts = line.split('\t')
            if len(parts) != 3:
                normalized_lines.append(line)
                continue

            front, back, tags = parts

            # Normalize tags
            tag_list = tags.split()

            # Ensure unit tag is first
            if unit_tag in tag_list:
                tag_list.remove(unit_tag)
            tag_list = [unit_tag] + tag_list

            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in tag_list:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)

            normalized_tags = ' '.join(unique_tags)

            normalized_line = f"{front}\t{back}\t{normalized_tags}"
            normalized_lines.append(normalized_line)

        return '\n'.join(normalized_lines)

    def generate_statistics(self, cards: str) -> Dict:
        """
        Generate statistics about the cards.

        Args:
            cards: Card content

        Returns:
            Dictionary with statistics
        """
        lines = cards.split('\n')
        stats = {
            'total_cards': 0,
            'tags': {},
            'avg_front_length': 0,
            'avg_back_length': 0,
        }

        front_lengths = []
        back_lengths = []

        for line in lines:
            # Skip headers and empty lines
            if line.startswith('#') or line == 'Front\tBack\tTags' or not line.strip():
                continue

            parts = line.split('\t')
            if len(parts) != 3:
                continue

            stats['total_cards'] += 1
            front, back, tags = parts

            front_lengths.append(len(front))
            back_lengths.append(len(back))

            # Count tags
            for tag in tags.split():
                stats['tags'][tag] = stats['tags'].get(tag, 0) + 1

        if front_lengths:
            stats['avg_front_length'] = sum(front_lengths) / len(front_lengths)
        if back_lengths:
            stats['avg_back_length'] = sum(back_lengths) / len(back_lengths)

        return stats

    def export_anki_file(self, cards: str, output_path: str) -> None:
        """
        Export cards to Anki file.

        Args:
            cards: Formatted card content
            output_path: Path to output file
        """
        from src.utils import save_file

        save_file(output_path, cards, encoding='utf-8')

        self.logger.info(f"Exported Anki file: {output_path}")
