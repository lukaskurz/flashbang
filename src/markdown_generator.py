"""
Markdown generation module for converting PDF content to markdown.
"""

import os
import logging
import re
from typing import List, Dict, Optional


class MarkdownGenerator:
    """Generate markdown documents from extracted PDF content."""

    def __init__(self, pages_data: List[Dict], images: List[Dict], unit_name: str):
        """
        Initialize markdown generator.

        Args:
            pages_data: List of page dictionaries from PDFProcessor
            images: List of image dictionaries from PDFProcessor
            unit_name: Name of the unit (for title)
        """
        self.logger = logging.getLogger(__name__)
        self.pages_data = pages_data
        self.images = images
        self.unit_name = unit_name

        # Create mapping of page numbers to images
        self.images_by_page = {}
        for img in images:
            page = img['page']
            if page not in self.images_by_page:
                self.images_by_page[page] = []
            self.images_by_page[page].append(img)

        # Load image descriptions from metadata
        self.image_descriptions = self._load_image_descriptions()

    def _load_image_descriptions(self) -> Dict[str, Dict]:
        """
        Load image descriptions from metadata storage.

        Returns:
            Dictionary mapping filename to metadata
        """
        try:
            from src.metadata.storage import MetadataStorage

            metadata_store = MetadataStorage()
            if metadata_store.load():
                # Get images for this unit
                unit_images = metadata_store.get_images_by_unit(self.unit_name)

                # Create mapping
                descriptions = {
                    img['filename']: img
                    for img in unit_images
                }

                if descriptions:
                    self.logger.info(
                        f"Loaded {len(descriptions)} image descriptions for {self.unit_name}"
                    )
                return descriptions
            else:
                self.logger.debug("No metadata found, images will have no descriptions")
                return {}

        except Exception as e:
            self.logger.debug(f"Failed to load image descriptions: {e}")
            return {}

    def generate_markdown(self) -> str:
        """
        Generate complete markdown document.

        Returns:
            Markdown content as string
        """
        md_parts = []

        # Title
        title = self._generate_title()
        md_parts.append(title)

        # Metadata
        md_parts.append(self._generate_metadata())

        # Table of Contents (placeholder for now)
        # md_parts.append(self._create_toc())

        # Content by pages
        content = self._generate_content()
        md_parts.append(content)

        # Image references section
        if self.images:
            md_parts.append(self._generate_image_references())

        markdown = "\n\n".join(md_parts)

        self.logger.info(f"Generated markdown with {len(markdown)} characters")
        return markdown

    def _generate_title(self) -> str:
        """Generate markdown title."""
        # Convert unit_name like "unit1_introduction" to "Unit 1: Introduction"
        title = self.unit_name.replace('_', ' ').title()
        return f"# {title}\n"

    def _generate_metadata(self) -> str:
        """Generate metadata section."""
        total_pages = len(self.pages_data)
        total_images = len(self.images)

        metadata = f"> **Pages:** {total_pages} | **Images:** {total_images}\n"
        return metadata

    def _generate_content(self) -> str:
        """
        Generate main content from pages.

        Returns:
            Markdown content
        """
        content_parts = []

        for page_data in self.pages_data:
            page_num = page_data['page_num']
            text = page_data['text']

            if not text.strip():
                continue

            # Add page marker
            content_parts.append(f"## Page {page_num}\n")

            # Process and format text
            formatted_text = self._format_text(text)
            content_parts.append(formatted_text)

            # Insert images for this page
            if page_num in self.images_by_page:
                image_refs = self._insert_image_references(page_num)
                if image_refs:
                    content_parts.append(image_refs)

        return "\n\n".join(content_parts)

    def _format_text(self, text: str) -> str:
        """
        Format text with markdown improvements.

        Args:
            text: Raw text from PDF

        Returns:
            Formatted markdown text
        """
        # Convert multiple newlines to double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Try to detect and format mathematical notation
        text = self._convert_math_notation(text)

        # Clean up excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    def _convert_math_notation(self, text: str) -> str:
        """
        Convert mathematical notation to MathJax format.

        Args:
            text: Text potentially containing math

        Returns:
            Text with MathJax formatting
        """
        # This is a simple heuristic-based conversion
        # More sophisticated conversion may be needed based on actual PDF content

        # Look for probability notation like P(X|Y) and wrap in inline math
        # text = re.sub(r'\bP\s*\([^)]+\)', lambda m: f'\\({m.group()}\\)', text)
        # text = re.sub(r'\bE\s*\[[^]]+\]', lambda m: f'\\({m.group()}\\)', text)

        # For now, we'll preserve the text as-is and let Claude handle math formatting
        # in the flashcard generation step

        return text

    def _insert_image_references(self, page_num: int) -> str:
        """
        Insert image references for a specific page with descriptions.

        Args:
            page_num: Page number

        Returns:
            Markdown image references with descriptions
        """
        if page_num not in self.images_by_page:
            return ""

        image_refs = []

        # Add section header
        page_images = self.images_by_page[page_num]
        if len(page_images) > 0:
            image_refs.append("### Available Images")

        for img in page_images:
            filename = img['filename']
            rel_path = f"../images/{filename}"

            # Create markdown image reference
            img_ref = f"![{filename}]({rel_path})"

            # Add description if available
            if filename in self.image_descriptions:
                metadata = self.image_descriptions[filename]
                description = metadata.get('description')
                img_type = metadata.get('type', 'diagram')
                contains_math = metadata.get('contains_math', False)

                if description:
                    math_indicator = "Math: yes" if contains_math else "Math: no"
                    desc_text = f"**Description:** {description} (Type: {img_type}, {math_indicator})"

                    img_ref = f"{img_ref}\n{desc_text}"

            image_refs.append(img_ref)

        if image_refs:
            return "\n\n" + "\n\n".join(image_refs)

        return ""

    def _generate_image_references(self) -> str:
        """
        Generate image references section at the end with descriptions.

        Returns:
            Markdown section with all images and descriptions
        """
        if not self.images:
            return ""

        refs = ["## Images Summary\n"]
        refs.append("All images extracted from this PDF:\n")

        for img in self.images:
            filename = img['filename']
            page = img['page']
            width = img.get('width', img.get('dimensions', {}).get('width', 0))
            height = img.get('height', img.get('dimensions', {}).get('height', 0))
            rel_path = f"../images/{filename}"

            # Basic reference
            ref = f"- [{filename}]({rel_path}) - Page {page} ({width}x{height})"

            # Add description if available
            if filename in self.image_descriptions:
                metadata = self.image_descriptions[filename]
                description = metadata.get('description')

                if description:
                    # Truncate description for summary
                    short_desc = description[:80] + "..." if len(description) > 80 else description
                    ref += f"\n  - {short_desc}"

            refs.append(ref)

        return "\n".join(refs)

    def create_toc(self, headings: List[str]) -> str:
        """
        Create table of contents from headings.

        Args:
            headings: List of heading strings

        Returns:
            Markdown table of contents
        """
        if not headings:
            return ""

        toc_parts = ["## Table of Contents\n"]

        for heading in headings:
            # Create anchor link
            anchor = heading.lower().replace(' ', '-').replace(':', '')
            # Remove special characters
            anchor = re.sub(r'[^\w\-]', '', anchor)

            toc_entry = f"- [{heading}](#{anchor})"
            toc_parts.append(toc_entry)

        return "\n".join(toc_parts)

    def format_section(self, heading: str, content: str, level: int = 2) -> str:
        """
        Format a section with heading and content.

        Args:
            heading: Section heading
            content: Section content
            level: Heading level (default: 2 for ##)

        Returns:
            Formatted markdown section
        """
        hashes = '#' * level
        return f"{hashes} {heading}\n\n{content}"
