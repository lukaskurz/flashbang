"""
Schema definitions for image metadata.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ImageMetadata:
    """
    Metadata for a single image.

    Attributes:
        filename: Image filename (e.g., 'unit1_page03_img01.png')
        unit: Unit name (e.g., 'unit1_introduction')
        page: Page number where image appears
        path: Absolute or relative path to image file
        dimensions: Image dimensions as {width, height}
        extracted_at: ISO timestamp when image was extracted
        description: AI-generated description (optional)
        type: Image type (network, algorithm, diagram, etc.)
        contains_math: Whether image contains mathematical notation
        described_at: ISO timestamp when description was generated
    """
    filename: str
    unit: str
    page: int
    path: str
    dimensions: Dict[str, int]
    extracted_at: str
    description: Optional[str] = None
    type: Optional[str] = None
    contains_math: Optional[bool] = None
    described_at: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ImageMetadata':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class MetadataCollection:
    """
    Collection of all image metadata.

    Attributes:
        version: Metadata format version
        generated_at: ISO timestamp when collection was created
        ollama_model: Ollama model used for descriptions
        images: Dictionary mapping filename to ImageMetadata
    """
    version: str
    generated_at: str
    ollama_model: str
    images: Dict[str, ImageMetadata]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'version': self.version,
            'generated_at': self.generated_at,
            'ollama_model': self.ollama_model,
            'images': {
                filename: img.to_dict() if isinstance(img, ImageMetadata) else img
                for filename, img in self.images.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MetadataCollection':
        """Create from dictionary."""
        images = {
            filename: ImageMetadata.from_dict(img_data) if isinstance(img_data, dict) else img_data
            for filename, img_data in data.get('images', {}).items()
        }

        return cls(
            version=data.get('version', '1.0'),
            generated_at=data.get('generated_at', datetime.now().isoformat()),
            ollama_model=data.get('ollama_model', 'ministral-3:8b'),
            images=images
        )

    def add_image(self, image_meta: ImageMetadata):
        """Add or update image metadata."""
        self.images[image_meta.filename] = image_meta

    def get_image(self, filename: str) -> Optional[ImageMetadata]:
        """Get image metadata by filename."""
        return self.images.get(filename)

    def get_images_by_unit(self, unit: str) -> List[ImageMetadata]:
        """Get all images for a specific unit."""
        return [
            img for img in self.images.values()
            if isinstance(img, ImageMetadata) and img.unit == unit
        ]

    def count(self) -> int:
        """Get total number of images."""
        return len(self.images)

    def count_described(self) -> int:
        """Get number of images with descriptions."""
        return sum(
            1 for img in self.images.values()
            if isinstance(img, ImageMetadata) and img.description is not None
        )
