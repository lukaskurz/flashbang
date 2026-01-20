"""
Abstract base class for flashcard generation providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable


class CardGenerationProvider(ABC):
    """Abstract base class for flashcard generation providers."""

    def __init__(self, config):
        """
        Initialize provider with config.

        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def generate_flashcards(
        self,
        unit_name: str,
        target_cards: int,
        output_dir: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Generate flashcards for a unit.

        Args:
            unit_name: Unit name
            target_cards: Target number of cards
            output_dir: Output directory
            progress_callback: Optional callback for progress updates

        Returns:
            Path to generated .txt file
        """
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check if provider is available and configured.

        Returns:
            True if provider is ready to use, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, str]:
        """
        Get provider information (name, model, version).

        Returns:
            Dictionary with provider metadata
        """
        pass

    @abstractmethod
    def validate_output(self, output_path: str) -> Dict[str, Any]:
        """
        Validate generated flashcard file.

        Args:
            output_path: Path to generated .txt file

        Returns:
            Dictionary with validation results
        """
        pass
