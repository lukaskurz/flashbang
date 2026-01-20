"""
Configuration management for PDF to Anki flashcard generation.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize configuration from YAML file.

        Args:
            config_path: Path to configuration YAML file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        self._validate_config(config)
        self.logger.info("Configuration loaded successfully")

        return config

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration has all required fields.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If required fields are missing
        """
        required_sections = ['processing', 'output', 'units']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate output directories
        for dir_key in ['markdown_dir', 'images_dir', 'anki_dir', 'apkg_dir']:
            if dir_key not in config['output']:
                raise ValueError(f"Missing output directory configuration: {dir_key}")

        # Validate units
        if not config['units']:
            raise ValueError("No units configured")

        self.logger.info("Configuration validation passed")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports dot notation).

        Args:
            key: Configuration key (e.g., 'api.model' or 'output.markdown_dir')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_unit_info(self, pdf_filename: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific PDF unit.

        Args:
            pdf_filename: Name of the PDF file

        Returns:
            Unit configuration dictionary or None if not found
        """
        units = self.config.get('units', {})
        return units.get(pdf_filename)

    def get_all_units(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all unit configurations.

        Returns:
            Dictionary mapping PDF filenames to unit configurations
        """
        return self.config.get('units', {})

    def get_unit_by_name(self, unit_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a unit by its unit_name.

        Args:
            unit_name: Unit name (e.g., 'unit1_introduction')

        Returns:
            Unit configuration dictionary or None if not found
        """
        units = self.get_all_units()
        for pdf_filename, unit_info in units.items():
            if unit_info.get('unit_name') == unit_name:
                return unit_info
        return None

    @property
    def extract_images(self) -> bool:
        """Whether to extract images."""
        return self.get('processing.extract_images', True)

    @property
    def min_image_size(self) -> tuple:
        """Minimum image size as (width, height)."""
        size = self.get('processing.min_image_size', [100, 100])
        return tuple(size)

    @property
    def image_format(self) -> str:
        """Image format."""
        return self.get('processing.image_format', 'png')

    @property
    def markdown_dir(self) -> str:
        """Markdown output directory."""
        return self.get('output.markdown_dir', 'outputs/markdown')

    @property
    def images_dir(self) -> str:
        """Images output directory."""
        return self.get('output.images_dir', 'outputs/images')

    @property
    def anki_dir(self) -> str:
        """Anki output directory."""
        return self.get('output.anki_dir', 'outputs/anki')

    @property
    def apkg_dir(self) -> str:
        """Anki package (APKG) output directory."""
        return self.get('output.apkg_dir', 'outputs/apkg')

    @property
    def card_distribution(self) -> Dict[str, float]:
        """Get card type distribution."""
        return self.get('card_distribution', {
            'conceptual': 0.40,
            'worked_examples': 0.20,
            'algorithm': 0.20,
            'pattern_recognition': 0.10,
            'visual': 0.10
        })

    @property
    def subject_name(self) -> str:
        """Get subject name."""
        return self.get('subject.name', 'Course Materials')

    @property
    def subject_short_name(self) -> str:
        """Get subject short name (used as deck prefix)."""
        return self.get('subject.short_name', 'Flashcards')

    @property
    def subject_field(self) -> str:
        """Get subject field (e.g., Mathematics, Computer Science)."""
        return self.get('subject.field', 'Education')

    @property
    def subject_description(self) -> str:
        """Get subject description."""
        return self.get('subject.description', 'Educational materials')

    def get_prompt_template(self, template_name: str) -> str:
        """
        Get prompt template with subject context interpolated.

        Args:
            template_name: Name of the prompt template (e.g., 'system_context')

        Returns:
            Formatted prompt string with {field}, {name}, {description} filled in
        """
        template = self.get(f'prompts.{template_name}', '')
        if not template:
            return ''

        return template.format(
            field=self.subject_field,
            name=self.subject_name,
            description=self.subject_description
        )

    def get_example_cards(self) -> List[Dict[str, str]]:
        """
        Get example cards from configuration.

        Returns:
            List of example card dictionaries with 'front', 'back', and 'tags' keys
        """
        examples = self.get('prompts.example_cards', [])
        if examples:
            return examples

        # Default examples if none configured
        return [
            {
                'front': 'Why does this algorithm avoid recomputing history?',
                'back': 'It uses <strong>recursive computation</strong> that only needs the previous state.',
                'tags': 'algorithm recursion'
            }
        ]

    def get_card_quality_focus(self) -> List[str]:
        """
        Get card quality guidelines from configuration.

        Returns:
            List of quality focus points
        """
        focus = self.get('prompts.card_quality_focus', [])
        if focus:
            return focus

        # Default quality guidelines
        return [
            'Test understanding, not memorization',
            'Use concrete examples',
            'Keep calculations simple',
            'Focus on concepts'
        ]


def load_config(config_path: str = 'config.yaml') -> Config:
    """
    Load configuration from file.

    Args:
        config_path: Path to configuration YAML file

    Returns:
        Config instance
    """
    return Config(config_path)
