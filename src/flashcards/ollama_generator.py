"""
Anki flashcard generator using Ollama.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from src.config import Config
from src.flashcards.base import CardGenerationProvider
from src.ollama.client import OllamaClient

logger = logging.getLogger(__name__)


class OllamaCardGenerator(CardGenerationProvider):
    """Generate Anki flashcards from markdown content using Ollama."""

    def __init__(self, config: Config = None):
        """
        Initialize flashcard generator.

        Args:
            config: Configuration object (uses default config if not provided)
        """
        # Initialize with config
        if config is None:
            config = Config()
        super().__init__(config)

        self.client = OllamaClient(
            base_url=self.config.ollama_generation_base_url,
            model=self.config.ollama_generation_model,
            timeout=self.config.ollama_generation_timeout,
            max_retries=self.config.ollama_generation_max_retries
        )

        self.temperature = self.config.ollama_generation_temperature

    def check_availability(self) -> bool:
        """Check if Ollama is available."""
        return self.client.check_availability()

    def get_provider_info(self) -> Dict[str, str]:
        """Get Ollama provider info."""
        return {
            'provider': 'ollama',
            'model': self.client.model,
            'base_url': self.client.base_url
        }

    def load_markdown(self, unit_name: str) -> str:
        """Load markdown content for a unit."""
        markdown_path = Path(self.config.markdown_dir) / f"{unit_name}.md"
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

        with open(markdown_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_image_metadata(self, unit_name: str) -> List[Dict]:
        """Load image descriptions for a unit."""
        metadata_path = Path("outputs/metadata/image_descriptions.json")

        if not metadata_path.exists():
            logger.warning("Image metadata not found")
            return []

        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Filter images for this unit
        unit_images = []
        for filename, img_data in data['images'].items():
            if img_data.get('unit') == unit_name:
                unit_images.append({
                    'filename': filename,
                    'page': img_data.get('page'),
                    'description': img_data.get('description'),
                    'type': img_data.get('type')
                })

        return unit_images

    def _format_quality_guidelines(self) -> str:
        """Format card quality guidelines from config."""
        guidelines = self.config.get_card_quality_focus()
        formatted = "Create cards that:\n"
        for i, guideline in enumerate(guidelines, 1):
            formatted += f"{i}. **{guideline}**\n"
        return formatted

    def _format_example_cards(self) -> str:
        """Format example cards from config."""
        examples = self.config.get_example_cards()
        if not examples:
            return ""

        formatted = ""
        for i, example in enumerate(examples, 1):
            formatted += f"**Example {i}:**\n```\n"
            formatted += f"Front: {example['front']}\n"
            formatted += f"Back: {example['back']}\n"
            formatted += f"Tags: {example['tags']}\n"
            formatted += "```\n\n"
        return formatted

    def _create_generation_prompt(
        self,
        markdown_content: str,
        images: List[Dict],
        target_cards: int
    ) -> str:
        """Create prompt for Ollama to generate flashcards."""

        # Get subject context from config
        subject_context = self.config.get_prompt_template('system_context')
        if not subject_context:
            subject_context = "You are generating educational flashcards."

        # Format image info
        image_context = ""
        if images:
            image_context = "\n\n## Available Images\n\n"
            for img in images:
                image_context += f"- **{img['filename']}** (Page {img['page']}, Type: {img['type']})\n"
                image_context += f"  Description: {img['description']}\n\n"

        # Get card distribution from config
        distribution = self.config.card_distribution
        dist_text = f"""- {int(distribution['conceptual']*100)}% Conceptual Understanding
- {int(distribution['worked_examples']*100)}% Simple Worked Examples
- {int(distribution['algorithm']*100)}% Algorithm Comprehension
- {int(distribution['pattern_recognition']*100)}% Pattern Recognition
- {int(distribution['visual']*100)}% Visual/Diagram-Based"""

        prompt = f"""{subject_context}

Your task is to generate exactly {target_cards} Anki flashcards from the lecture content below.

# Lecture Content

{markdown_content[:15000]}
{image_context}

# CRITICAL OUTPUT FORMAT REQUIREMENTS

You MUST output ONLY the flashcard data in this exact format:

First, these header lines:
#separator:tab
#html:true
#tags column:3
Front	Back	Tags

Then each flashcard as a single line with THREE tab-separated columns:
Front[TAB]Back[TAB]Tags

IMPORTANT FORMATTING RULES:
- Use actual TAB characters to separate columns (not spaces)
- Use <br> for line breaks within fields (not \\n)
- Use <strong> for bold text
- Use \\(...\\) for inline math, \\[...\\] for display math
- Place images in Front using: <img src="filename.png" style="max-width:500px;">
- Tags should be space-separated words
- Each card must be on a SINGLE line
- NO explanatory text before or after the flashcards
- Start directly with the headers

# Card Quality Guidelines

{self._format_quality_guidelines()}

# Card Type Distribution

Generate approximately:
{dist_text}

# Example Cards Format

{self._format_example_cards()}

# Your Task

Generate exactly {target_cards} flashcards following the format above.

OUTPUT ONLY:
1. The four header lines
2. {target_cards} flashcard lines (Front[TAB]Back[TAB]Tags)

Nothing else. No introductions, no explanations, no markdown formatting around the output.
"""
        return prompt

    def generate_flashcards(
        self,
        unit_name: str,
        target_cards: int = 60,
        output_dir: str = "outputs"
    ) -> str:
        """
        Generate Anki flashcards for a unit using Ollama.

        Args:
            unit_name: Unit name (e.g., 'unit3_core_topics')
            target_cards: Target number of flashcards to generate
            output_dir: Output directory for .txt file

        Returns:
            Path to generated .txt file
        """
        logger.info(f"Generating flashcards for {unit_name} using Ollama")

        # Load content
        markdown_content = self.load_markdown(unit_name)
        images = self.load_image_metadata(unit_name)

        # Create prompt
        prompt = self._create_generation_prompt(
            markdown_content,
            images,
            target_cards
        )

        # Generate using Ollama
        logger.info(f"Calling Ollama ({self.client.model}) to generate ~{target_cards} flashcards...")

        flashcard_content = self.client.generate_text(
            prompt=prompt,
            temperature=self.temperature
        )

        if not flashcard_content:
            raise RuntimeError("Ollama failed to generate flashcards")

        # Save to file
        output_path = Path(output_dir) / f"{unit_name}_anki.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(flashcard_content)

        logger.info(f"Saved flashcards to {output_path}")
        return str(output_path)

    def validate_output(self, output_path: str) -> Dict[str, Any]:
        """
        Validate generated flashcard file.

        Args:
            output_path: Path to generated .txt file

        Returns:
            Dictionary with validation results
        """
        with open(output_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'card_count': 0,
            'has_headers': False
        }

        # Check headers
        if len(lines) < 4:
            results['valid'] = False
            results['errors'].append("File too short - missing headers")
            return results

        if lines[0].strip() != '#separator:tab':
            results['errors'].append("Missing #separator:tab header")
        if lines[1].strip() != '#html:true':
            results['errors'].append("Missing #html:true header")
        if lines[2].strip() != '#tags column:3':
            results['errors'].append("Missing #tags column:3 header")
        if not lines[3].startswith('Front\tBack\tTags'):
            results['errors'].append("Missing column headers")
        else:
            results['has_headers'] = True

        # Count cards (skip header lines)
        results['card_count'] = len(lines) - 4

        # Check for common issues
        for i, line in enumerate(lines[4:], start=5):
            if line.strip():
                # Check for proper tab separation
                parts = line.split('\t')
                if len(parts) != 3:
                    results['warnings'].append(f"Line {i}: Expected 3 columns, got {len(parts)}")

        if results['errors']:
            results['valid'] = False

        return results
