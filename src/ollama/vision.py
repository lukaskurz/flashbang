"""
Vision-specific logic for image description using Ollama.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console

from src.ollama.client import OllamaClient
from src.ollama.prompts import get_image_description_prompt
from src.config import Config

logger = logging.getLogger(__name__)


def describe_image(
    image_path: str,
    page_number: Optional[int] = None,
    unit_name: Optional[str] = None,
    client: Optional[OllamaClient] = None,
    config: Optional[Config] = None
) -> Optional[str]:
    """
    Generate description for a single image.

    Args:
        image_path: Path to image file
        page_number: Optional page number for context
        unit_name: Optional unit name for extracting page context
        client: Optional OllamaClient instance (creates new one if None)
        config: Optional Config instance for subject context

    Returns:
        Image description string, or None if failed
    """
    if client is None:
        client = OllamaClient()

    if config is None:
        config = Config()

    # Check if Ollama is available
    if not client.check_availability():
        logger.warning("Ollama not available, skipping description")
        return None

    # Extract page context if unit info available
    page_context = None
    if unit_name and page_number:
        from src.ollama.context import extract_page_text
        try:
            page_context = extract_page_text(unit_name, page_number)
        except Exception as e:
            logger.warning(f"Failed to extract page context: {e}")

    # Get subject context from config
    subject_context = config.get('ollama.subject_context', f'{config.subject_field} lecture slides')

    # Generate prompt with context
    prompt = get_image_description_prompt(page_number, page_context, subject_context)

    try:
        # Get description
        description = client.generate_with_image(prompt, image_path)

        if description:
            logger.info(f"Generated description for {Path(image_path).name}")
            return description
        else:
            logger.warning(f"Failed to generate description for {Path(image_path).name}")
            return None

    except Exception as e:
        logger.error(f"Error describing {Path(image_path).name}: {e}")
        return None


def describe_images_batch(
    metadata_store,
    client: Optional[OllamaClient] = None,
    console: Optional[Console] = None,
    progress: bool = True,
    config: Optional[Config] = None
) -> int:
    """
    Generate descriptions for all images in metadata store.

    Args:
        metadata_store: MetadataStorage instance
        client: Optional OllamaClient instance
        console: Optional Rich Console for output
        progress: Whether to show progress bar
        config: Optional Config instance for subject context

    Returns:
        Number of images successfully described
    """
    if client is None:
        client = OllamaClient()

    if console is None:
        console = Console()

    if config is None:
        config = Config()

    # Get images without descriptions
    all_images = metadata_store.get_all_images()
    undescribed = [img for img in all_images if not img.get('description')]

    if not undescribed:
        logger.info("All images already have descriptions")
        return 0

    logger.info(f"Describing {len(undescribed)} images...")

    described_count = 0

    if progress:
        # Process with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as prog:

            task = prog.add_task(
                "[cyan]Describing images...",
                total=len(undescribed)
            )

            for img in undescribed:
                filename = img['filename']
                image_path = img['path']
                page = img.get('page')
                unit = img.get('unit')

                prog.update(task, description=f"[cyan]Describing {filename}...")

                try:
                    description = describe_image(image_path, page, unit, client, config)

                    if description:
                        # Extract type and math info from description
                        img_type = extract_type_from_description(description)
                        contains_math = 'yes' in description.lower() or 'math' in description.lower()

                        # Update metadata
                        metadata_store.update_description(
                            filename,
                            description,
                            img_type=img_type,
                            contains_math=contains_math
                        )

                        described_count += 1
                    else:
                        logger.warning(f"Skipping {filename} - no description generated")

                except Exception as e:
                    logger.error(f"Failed to describe {filename}: {e}")

                prog.advance(task)

    else:
        # Process without progress bar
        for img in undescribed:
            filename = img['filename']
            image_path = img['path']
            page = img.get('page')
            unit = img.get('unit')

            try:
                description = describe_image(image_path, page, unit, client, config)

                if description:
                    img_type = extract_type_from_description(description)
                    contains_math = 'yes' in description.lower() or 'math' in description.lower()

                    metadata_store.update_description(
                        filename,
                        description,
                        img_type=img_type,
                        contains_math=contains_math
                    )

                    described_count += 1

            except Exception as e:
                logger.error(f"Failed to describe {filename}: {e}")

    logger.info(f"Successfully described {described_count}/{len(undescribed)} images")

    return described_count


def extract_type_from_description(description: str) -> str:
    """
    Extract image type from description text.

    Args:
        description: Image description

    Returns:
        Image type (network, algorithm, diagram, etc.)
    """
    description_lower = description.lower()

    # Check for specific types
    type_keywords = {
        'network': ['bayesian network', 'network diagram', 'network structure'],
        'algorithm': ['algorithm', 'flowchart', 'flow chart', 'pseudocode'],
        'formula': ['formula', 'equation', 'mathematical expression'],
        'table': ['table', 'comparison table', 'matrix'],
        'graph': ['graph', 'plot', 'chart'],
        'example': ['example', 'worked example', 'problem']
    }

    for img_type, keywords in type_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            return img_type

    # Default type
    return 'diagram'


def categorize_image(
    image_path: str,
    client: Optional[OllamaClient] = None
) -> Dict[str, any]:
    """
    Quick categorization of image without full description.

    Args:
        image_path: Path to image file
        client: Optional OllamaClient instance

    Returns:
        Dictionary with type, topic, and math info
    """
    if client is None:
        client = OllamaClient()

    from src.ollama.prompts import get_quick_categorization_prompt

    prompt = get_quick_categorization_prompt()

    try:
        response = client.generate_with_image(prompt, image_path)

        if response:
            # Parse response
            lines = response.strip().split('\n')
            result = {
                'type': 'unknown',
                'topic': 'unknown',
                'contains_math': False
            }

            for line in lines:
                if 'type:' in line.lower():
                    result['type'] = line.split(':', 1)[1].strip()
                elif 'topic:' in line.lower():
                    result['topic'] = line.split(':', 1)[1].strip()
                elif 'math:' in line.lower():
                    result['contains_math'] = 'yes' in line.lower()

            return result

    except Exception as e:
        logger.error(f"Failed to categorize image: {e}")

    return {'type': 'unknown', 'topic': 'unknown', 'contains_math': False}
