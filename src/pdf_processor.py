"""
PDF processing module for extracting text and images.
"""

import os
import io
import logging
from typing import List, Dict, Tuple
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


class PDFProcessor:
    """Extract text and images from PDF files."""

    def __init__(self, pdf_path: str, unit_name: str = None):
        """
        Initialize PDF processor.

        Args:
            pdf_path: Path to PDF file
            unit_name: Name of the unit (for image naming)
        """
        self.logger = logging.getLogger(__name__)
        self.pdf_path = pdf_path
        self.unit_name = unit_name or Path(pdf_path).stem
        self.doc = None
        self._open_pdf()

    def _open_pdf(self) -> None:
        """Open PDF document."""
        try:
            self.doc = fitz.open(self.pdf_path)
            self.logger.info(f"Opened PDF: {self.pdf_path} ({self.doc.page_count} pages)")
        except Exception as e:
            self.logger.error(f"Failed to open PDF {self.pdf_path}: {e}")
            raise

    def close(self) -> None:
        """Close PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def extract_text_by_page(self) -> List[Dict]:
        """
        Extract text from PDF page by page.

        Returns:
            List of dictionaries with page information:
            [{"page_num": 1, "text": "...", "has_images": True}, ...]
        """
        pages_data = []

        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]

            try:
                # Extract text with layout preservation
                text = page.get_text("text")

                # Check if page has images
                images = page.get_images()
                has_images = len(images) > 0

                pages_data.append({
                    "page_num": page_num + 1,  # 1-indexed
                    "text": text,
                    "has_images": has_images,
                    "image_count": len(images)
                })

                self.logger.debug(
                    f"Page {page_num + 1}: {len(text)} chars, {len(images)} images"
                )

            except Exception as e:
                self.logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                pages_data.append({
                    "page_num": page_num + 1,
                    "text": "",
                    "has_images": False,
                    "image_count": 0,
                    "error": str(e)
                })

        self.logger.info(f"Extracted text from {len(pages_data)} pages")
        return pages_data

    def extract_images(
        self,
        output_dir: str,
        min_size: Tuple[int, int] = (100, 100)
    ) -> List[Dict]:
        """
        Extract images from PDF with enhanced metadata.

        Args:
            output_dir: Directory to save images
            min_size: Minimum image size (width, height) to extract

        Returns:
            List of dictionaries with image information:
            [{"page": 1, "path": "...", "filename": "...", "dimensions": {...},
              "extracted_at": "...", ...}, ...]
        """
        from datetime import datetime
        from src.utils import ensure_dir

        ensure_dir(output_dir)
        extracted_images = []
        image_counter = 1

        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]
            images = page.get_images()

            for img_index, img_info in enumerate(images):
                try:
                    xref = img_info[0]
                    img_data = self._extract_image_data(xref)

                    if not img_data:
                        continue

                    img_obj, width, height = img_data

                    # Filter by minimum size
                    if width < min_size[0] or height < min_size[1]:
                        self.logger.debug(
                            f"Skipping small image on page {page_num + 1}: {width}x{height}"
                        )
                        continue

                    # Generate filename: unit1_page03_img01.png
                    filename = f"{self.unit_name}_page{page_num + 1:02d}_img{image_counter:02d}.png"
                    filepath = os.path.join(output_dir, filename)

                    # Save image
                    img_obj.save(filepath, format='PNG')

                    # Enhanced metadata
                    extracted_images.append({
                        "filename": filename,
                        "page": page_num + 1,
                        "path": filepath,
                        "image_path": filepath,  # Backwards compatibility
                        "dimensions": {
                            "width": width,
                            "height": height
                        },
                        "width": width,  # Backwards compatibility
                        "height": height,  # Backwards compatibility
                        "extracted_at": datetime.now().isoformat(),
                        "unit": self.unit_name
                    })

                    self.logger.debug(f"Extracted image: {filename} ({width}x{height})")
                    image_counter += 1

                except Exception as e:
                    self.logger.warning(
                        f"Failed to extract image {img_index} from page {page_num + 1}: {e}"
                    )

        self.logger.info(f"Extracted {len(extracted_images)} images")
        return extracted_images

    def _extract_image_data(self, xref: int) -> Tuple:
        """
        Extract image data from xref.

        Args:
            xref: Image cross-reference number

        Returns:
            Tuple of (PIL.Image, width, height) or None if failed
        """
        try:
            base_image = self.doc.extract_image(xref)
            img_bytes = base_image["image"]

            # Open with PIL
            img = Image.open(io.BytesIO(img_bytes))

            # Convert to RGB if necessary (for PNG output)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            width, height = img.size
            return img, width, height

        except Exception as e:
            self.logger.debug(f"Failed to extract image data for xref {xref}: {e}")
            return None

    def detect_headings(self, page_text: str) -> List[str]:
        """
        Detect potential headings from page text using simple heuristics.

        Args:
            page_text: Text from a page

        Returns:
            List of potential heading lines
        """
        headings = []
        lines = page_text.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Heuristics for headings:
            # 1. All caps and reasonably short
            # 2. Ends with colon
            # 3. Contains common heading words

            is_heading = False

            # All caps and short (likely a section heading)
            if line.isupper() and 5 < len(line) < 80:
                is_heading = True

            # Contains heading indicators
            heading_indicators = [
                'Chapter', 'Section', 'Unit', 'Lecture',
                'Introduction', 'Overview', 'Summary',
                'Definition', 'Theorem', 'Lemma', 'Proof'
            ]

            for indicator in heading_indicators:
                if line.startswith(indicator):
                    is_heading = True
                    break

            if is_heading:
                headings.append(line)

        return headings

    def extract_mathematical_content(self, text: str) -> List[str]:
        """
        Identify potential mathematical formulas and equations.

        Args:
            text: Text content

        Returns:
            List of lines that likely contain mathematical notation
        """
        import re

        math_lines = []
        lines = text.split('\n')

        # Patterns that suggest mathematical content
        math_patterns = [
            r'[=≠≈∝∈∉⊂⊃∩∪∀∃]',  # Math symbols
            r'[α-ωΑ-Ω]',  # Greek letters
            r'\b[PpEe]\s*\(',  # Probability notation P(...), E(...)
            r'∑|∏|∫|∂',  # Summation, product, integral, partial
            r'\^\s*\d+',  # Superscripts
            r'_\s*\d+',  # Subscripts
        ]

        combined_pattern = '|'.join(math_patterns)

        for line in lines:
            if re.search(combined_pattern, line):
                math_lines.append(line.strip())

        return math_lines

    def get_page_count(self) -> int:
        """Get total number of pages."""
        return self.doc.page_count if self.doc else 0

    def get_metadata(self) -> Dict:
        """
        Get PDF metadata.

        Returns:
            Dictionary with PDF metadata
        """
        if not self.doc:
            return {}

        metadata = {
            "page_count": self.doc.page_count,
            "title": self.doc.metadata.get("title", ""),
            "author": self.doc.metadata.get("author", ""),
            "subject": self.doc.metadata.get("subject", ""),
        }

        return metadata
