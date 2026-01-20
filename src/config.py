"""
Configuration management for PDF to Anki flashcard generation.
"""

import os
import re
import yaml
import logging
from pathlib import Path
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
        # Required sections (units is now optional due to auto-discovery)
        required_sections = ['processing', 'output']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate output directories
        for dir_key in ['markdown_dir', 'images_dir', 'anki_dir', 'apkg_dir']:
            if dir_key not in config['output']:
                raise ValueError(f"Missing output directory configuration: {dir_key}")

        # Check if we have either configured units OR PDFs in directory
        configured_units = config.get('units', {})
        discovered_pdfs = self.discover_pdfs()

        if not configured_units and not discovered_pdfs:
            raise ValueError(
                "No units configured and no PDFs found in pdfs/ directory. "
                "Either add PDFs to pdfs/ or configure units in config.yaml"
            )

        self.logger.info("Configuration validation passed")

    def discover_pdfs(self, pdfs_dir: str = "pdfs") -> List[str]:
        """
        Discover PDF files in directory.

        Args:
            pdfs_dir: Directory containing PDF files

        Returns:
            List of PDF filenames (sorted)
        """
        pdfs_path = Path(pdfs_dir)
        if not pdfs_path.exists():
            self.logger.warning(f"PDFs directory not found: {pdfs_dir}")
            return []

        pdf_files = sorted([f.name for f in pdfs_path.glob("*.pdf")])
        self.logger.debug(f"Discovered {len(pdf_files)} PDF files in {pdfs_dir}")
        return pdf_files

    def generate_unit_name(self, pdf_filename: str) -> str:
        """
        Generate default unit name from PDF filename.

        Examples:
            "Intro.pdf" → "unit_intro"
            "Unit_1.pdf" → "unit_1"
            "lecture 3.pdf" → "unit_lecture_3"
            "Unit 1.pdf" → "unit_1"

        Args:
            pdf_filename: PDF filename (e.g., "Unit_1.pdf")

        Returns:
            Generated unit name (e.g., "unit_1")
        """
        # Remove .pdf extension
        name = pdf_filename.replace('.pdf', '').replace('.PDF', '')

        # Convert to lowercase
        name = name.lower()

        # Replace spaces, hyphens, dots with underscores
        name = re.sub(r'[\s\-\.]+', '_', name)

        # Remove any non-alphanumeric characters except underscores
        name = re.sub(r'[^\w]', '', name)

        # Remove leading/trailing underscores
        name = name.strip('_')

        # Prepend unit_ if not already present
        if not name.startswith('unit'):
            name = f'unit_{name}'

        return name

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
        Get all unit configurations (auto-discovered + configured).

        Auto-discovers PDFs from pdfs/ directory and merges with explicit
        configuration. Configured values take precedence over auto-discovered.

        Returns:
            Dictionary mapping PDF filenames to unit configurations.
            Each unit dict includes:
                - unit_name: str
                - target_cards: int
                - tags: List[str]
                - source: str ('auto-discovered', 'configured', or 'configured-only')
        """
        # Get default target cards
        default_target_cards = self.default_target_cards

        # Discover PDFs
        discovered_pdfs = self.discover_pdfs()
        units = {}

        # Create entries for auto-discovered PDFs
        for pdf_file in discovered_pdfs:
            unit_name = self.generate_unit_name(pdf_file)
            units[pdf_file] = {
                'unit_name': unit_name,
                'target_cards': default_target_cards,
                'tags': [unit_name],
                'source': 'auto-discovered'
            }

        # Merge with explicit configuration (configured values take precedence)
        configured_units = self.config.get('units', {})
        for pdf_file, overrides in configured_units.items():
            if pdf_file in units:
                # Update discovered unit with configured values
                units[pdf_file].update(overrides)
                units[pdf_file]['source'] = 'configured'
            else:
                # PDF in config but not found in directory
                # Still include it for backward compatibility
                units[pdf_file] = overrides.copy()
                units[pdf_file]['source'] = 'configured-only'
                if pdf_file not in discovered_pdfs:
                    self.logger.warning(
                        f"PDF '{pdf_file}' is configured but not found in pdfs/ directory"
                    )

        return units

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
    def default_target_cards(self) -> int:
        """Get default target cards for auto-discovered units."""
        return self.get('defaults.target_cards', 50)

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
    def metadata_dir(self) -> str:
        """Metadata output directory."""
        return self.get('output.metadata_dir', 'outputs/metadata')

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

    @property
    def generation_provider(self) -> str:
        """Get card generation provider (claude or ollama)."""
        return self.get('generation.provider', 'claude')

    @property
    def claude_model(self) -> str:
        """Get Claude model name."""
        return self.get('generation.claude.model', 'claude-sonnet-4-20250514')

    @property
    def claude_api_key_env(self) -> str:
        """Get Claude API key environment variable name."""
        return self.get('generation.claude.api_key_env', 'ANTHROPIC_API_KEY')

    @property
    def claude_max_tokens(self) -> int:
        """Get Claude max tokens."""
        return self.get('generation.claude.max_tokens', 16000)

    @property
    def ollama_generation_base_url(self) -> str:
        """Get Ollama base URL for card generation."""
        return self.get('generation.ollama.base_url', 'http://localhost:11434')

    @property
    def ollama_generation_model(self) -> str:
        """Get Ollama model for card generation."""
        return self.get('generation.ollama.model', 'ministral-3:14b')

    @property
    def ollama_generation_timeout(self) -> int:
        """Get Ollama timeout for card generation."""
        return self.get('generation.ollama.timeout', 120)

    @property
    def ollama_generation_max_retries(self) -> int:
        """Get Ollama max retries for card generation."""
        return self.get('generation.ollama.max_retries', 3)

    @property
    def ollama_generation_temperature(self) -> float:
        """Get Ollama temperature for card generation."""
        return self.get('generation.ollama.temperature', 0.7)

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
