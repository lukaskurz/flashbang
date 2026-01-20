"""
JSON-based storage for image metadata.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from PIL import Image

from src.metadata.schema import ImageMetadata, MetadataCollection

logger = logging.getLogger(__name__)


class MetadataStorage:
    """
    Manages persistent storage of image metadata in JSON format.

    Attributes:
        metadata_file: Path to JSON metadata file
        collection: In-memory metadata collection
    """

    def __init__(self, metadata_file: str = "outputs/metadata/image_descriptions.json"):
        """
        Initialize metadata storage.

        Args:
            metadata_file: Path to JSON file for storing metadata
        """
        self.metadata_file = Path(metadata_file)
        self.collection: Optional[MetadataCollection] = None

        # Ensure directory exists
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing metadata if available
        self.load()

    def load(self) -> bool:
        """
        Load metadata from JSON file.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.metadata_file.exists():
            logger.info(f"Metadata file not found, creating new collection")
            self._create_new_collection()
            return False

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.collection = MetadataCollection.from_dict(data)
            logger.info(f"Loaded {self.collection.count()} images from {self.metadata_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self._create_new_collection()
            return False

    def save(self, backup: bool = True) -> bool:
        """
        Save metadata to JSON file.

        Args:
            backup: Whether to create backup of existing file

        Returns:
            True if saved successfully, False otherwise
        """
        if self.collection is None:
            logger.warning("No collection to save")
            return False

        try:
            # Backup existing file
            if backup and self.metadata_file.exists():
                backup_path = self.metadata_file.with_suffix('.json.bak')
                self.metadata_file.rename(backup_path)
                logger.debug(f"Created backup: {backup_path}")

            # Update generated_at timestamp
            self.collection.generated_at = datetime.now().isoformat()

            # Write to file
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.collection.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {self.collection.count()} images to {self.metadata_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return False

    def add_images(self, images: List[Dict], unit: str = None):
        """
        Add multiple images to metadata.

        Args:
            images: List of image dictionaries from pdf_processor
            unit: Override unit name for all images
        """
        if self.collection is None:
            self._create_new_collection()

        for img_data in images:
            try:
                # Extract dimensions if image file exists
                dimensions = img_data.get('dimensions', {'width': 0, 'height': 0})

                if not dimensions or dimensions.get('width', 0) == 0:
                    # Try to read from file
                    img_path = img_data.get('path') or img_data.get('filename')
                    if img_path and Path(img_path).exists():
                        try:
                            with Image.open(img_path) as pil_img:
                                dimensions = {'width': pil_img.width, 'height': pil_img.height}
                        except Exception as e:
                            logger.debug(f"Could not read image dimensions: {e}")
                            dimensions = {'width': 0, 'height': 0}

                # Create metadata object
                image_meta = ImageMetadata(
                    filename=img_data.get('filename', ''),
                    unit=unit or img_data.get('unit', ''),
                    page=img_data.get('page', 0),
                    path=img_data.get('path', img_data.get('filename', '')),
                    dimensions=dimensions,
                    extracted_at=img_data.get('extracted_at', datetime.now().isoformat()),
                    description=img_data.get('description'),
                    type=img_data.get('type'),
                    contains_math=img_data.get('contains_math'),
                    described_at=img_data.get('described_at')
                )

                self.collection.add_image(image_meta)

            except Exception as e:
                logger.error(f"Failed to add image {img_data.get('filename', 'unknown')}: {e}")

    def update_description(
        self,
        filename: str,
        description: str,
        img_type: Optional[str] = None,
        contains_math: Optional[bool] = None
    ):
        """
        Update description for an image.

        Args:
            filename: Image filename
            description: Description text
            img_type: Image type (network, algorithm, etc.)
            contains_math: Whether image contains math
        """
        if self.collection is None:
            logger.warning("No collection loaded")
            return

        image_meta = self.collection.get_image(filename)

        if image_meta:
            image_meta.description = description
            image_meta.described_at = datetime.now().isoformat()

            if img_type:
                image_meta.type = img_type

            if contains_math is not None:
                image_meta.contains_math = contains_math

            logger.debug(f"Updated description for {filename}")
        else:
            logger.warning(f"Image {filename} not found in metadata")

    def get_all_images(self) -> List[Dict]:
        """
        Get all images as dictionaries.

        Returns:
            List of image metadata dictionaries
        """
        if self.collection is None:
            return []

        return [
            img.to_dict() if isinstance(img, ImageMetadata) else img
            for img in self.collection.images.values()
        ]

    def get_images_by_unit(self, unit: str) -> List[Dict]:
        """
        Get all images for a specific unit.

        Args:
            unit: Unit name

        Returns:
            List of image metadata dictionaries
        """
        if self.collection is None:
            return []

        unit_images = self.collection.get_images_by_unit(unit)
        return [img.to_dict() for img in unit_images]

    def get_undescribed_images(self) -> List[Dict]:
        """
        Get all images without descriptions.

        Returns:
            List of image metadata dictionaries
        """
        if self.collection is None:
            return []

        return [
            img.to_dict() if isinstance(img, ImageMetadata) else img
            for img in self.collection.images.values()
            if isinstance(img, ImageMetadata) and img.description is None
        ]

    def get_stats(self) -> Dict:
        """
        Get metadata statistics.

        Returns:
            Dictionary with statistics
        """
        if self.collection is None:
            return {
                'total_images': 0,
                'described_images': 0,
                'undescribed_images': 0,
                'percentage_described': 0.0
            }

        total = self.collection.count()
        described = self.collection.count_described()

        return {
            'total_images': total,
            'described_images': described,
            'undescribed_images': total - described,
            'percentage_described': (described / total * 100) if total > 0 else 0.0
        }

    def _create_new_collection(self):
        """Create a new empty metadata collection."""
        self.collection = MetadataCollection(
            version="1.0",
            generated_at=datetime.now().isoformat(),
            ollama_model="ministral-3:8b",
            images={}
        )
        logger.info("Created new metadata collection")
