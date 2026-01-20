"""
Factory for creating flashcard generation providers.
"""

from src.flashcards.base import CardGenerationProvider
from src.flashcards.generator import ClaudeCardGenerator
from src.flashcards.ollama_generator import OllamaCardGenerator
from src.config import Config
from typing import Optional


def create_card_generator(
    config: Config = None,
    provider: Optional[str] = None
) -> CardGenerationProvider:
    """
    Create a card generator based on configuration.

    Args:
        config: Configuration object (uses default if None)
        provider: Override provider ('claude' or 'ollama'), uses config if None

    Returns:
        CardGenerationProvider instance

    Raises:
        ValueError: If provider is unknown
        RuntimeError: If provider is unavailable
    """
    if config is None:
        config = Config()

    provider_name = provider or config.generation_provider

    if provider_name == 'claude':
        generator = ClaudeCardGenerator(config)
    elif provider_name == 'ollama':
        generator = OllamaCardGenerator(config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Must be 'claude' or 'ollama'")

    # Check availability
    if not generator.check_availability():
        info = generator.get_provider_info()
        raise RuntimeError(
            f"Provider '{provider_name}' is not available. "
            f"Model: {info.get('model')}. "
            f"Check configuration and ensure service is running."
        )

    return generator
