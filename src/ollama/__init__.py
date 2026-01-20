"""
Ollama integration package for image description using vision models.
"""

from src.ollama.client import OllamaClient
from src.ollama.vision import describe_image, describe_images_batch

__all__ = ['OllamaClient', 'describe_image', 'describe_images_batch']
