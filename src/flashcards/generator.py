"""
Anki flashcard generator using Claude API.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
import anthropic
import os
from src.config import Config
from src.flashcards.base import CardGenerationProvider

logger = logging.getLogger(__name__)


class ClaudeCardGenerator(CardGenerationProvider):
    """Generate Anki flashcards from markdown content using Claude."""

    def __init__(self, config: Config = None, api_key: Optional[str] = None):
        """
        Initialize flashcard generator.

        Args:
            config: Configuration object (uses default config if not provided)
            api_key: Optional Anthropic API key (uses env var from config if not provided)
        """
        # Initialize with config
        if config is None:
            config = Config()
        super().__init__(config)

        # Get API key from env var specified in config
        api_key_env = self.config.claude_api_key_env
        self.api_key = api_key or os.getenv(api_key_env)

        if not self.api_key:
            raise ValueError(f"{api_key_env} not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = self.config.claude_model
        self.max_tokens = self.config.claude_max_tokens

    def check_availability(self) -> bool:
        """Check if Claude API is available."""
        return self.api_key is not None

    def get_provider_info(self) -> Dict[str, str]:
        """Get Claude provider info."""
        return {
            'provider': 'claude',
            'model': self.model,
            'max_tokens': str(self.max_tokens)
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
        metadata_path = Path(self.config.metadata_dir) / "image_descriptions.json"

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

    def generate_flashcards(
        self,
        unit_name: str,
        target_cards: int = 60,
        output_dir: str = "outputs",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Generate Anki flashcards for a unit.

        Args:
            unit_name: Unit name (e.g., 'unit3_core_topics')
            target_cards: Target number of flashcards to generate
            output_dir: Output directory for .txt file
            progress_callback: Optional callback for progress updates

        Returns:
            Path to generated .txt file
        """
        logger.info(f"Generating flashcards for {unit_name}")

        # Load content
        markdown_content = self.load_markdown(unit_name)
        images = self.load_image_metadata(unit_name)

        # Create prompt for Claude
        prompt = self._create_generation_prompt(
            markdown_content,
            images,
            target_cards
        )

        # Generate flashcards using Claude
        logger.info(f"Calling Claude API to generate ~{target_cards} flashcards...")

        if progress_callback:
            # Use streaming for progress feedback
            flashcard_content = ""
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            ) as stream:
                for text in stream.text_stream:
                    flashcard_content += text
                    progress_callback(text)
        else:
            # Non-streaming mode
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            flashcard_content = response.content[0].text

        # Save to file
        output_path = Path(output_dir) / f"{unit_name}_anki.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(flashcard_content)

        logger.info(f"Saved flashcards to {output_path}")
        return str(output_path)

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
        """Create prompt for Claude to generate flashcards."""

        # Get subject context from config
        subject_context = self.config.get_prompt_template('system_context')
        if not subject_context:
            subject_context = "You are generating educational flashcards from lecture materials."

        # Format image info
        image_context = ""
        if images:
            image_context = "\n\n## Available Images\n\n"
            for img in images:
                image_context += f"- **{img['filename']}** (Page {img['page']}, Type: {img['type']})\n"
                image_context += f"  Description: {img['description']}\n\n"

        # Get card distribution from config
        distribution = self.config.card_distribution
        dist_text = f"""- {int(distribution['conceptual']*100)}% Conceptual Understanding (Why does X work? What's the intuition?)
- {int(distribution['worked_examples']*100)}% Simple Worked Examples (Tiny scenarios, obvious answers)
- {int(distribution['algorithm']*100)}% Algorithm Comprehension (What does this step do? Why avoid problem X?)
- {int(distribution['pattern_recognition']*100)}% Pattern Recognition (Identify reasoning patterns, independence structures)
- {int(distribution['visual']*100)}% Visual/Diagram-Based (with images in the question)"""

        prompt = f"""{subject_context}

Generate approximately {target_cards} Anki flashcards from the following lecture content.

# Content Source

{markdown_content[:20000]}
{image_context}

# Output Format Requirements

Generate a tab-separated text file with these exact headers:
```
#separator:tab
#html:true
#tags column:3
Front	Back	Tags
```

Each flashcard row should have:
- **Front**: The question (use <br> for line breaks, not \\n)
- **Back**: The answer with explanation (use <br> for line breaks, not \\n)
- **Tags**: Space-separated tags (e.g., "core-topics methods")

# Formatting Guidelines

1. **MathJax**: Use `\\(...\\)` for inline math, `\\[...\\]` for display math
2. **HTML**: Use `<strong>` for emphasis, `<br>` for line breaks, `<ul>` and `<li>` for lists
3. **Images**: Reference images using `<img src="filename.png" style="max-width:500px;">`
   - **IMPORTANT**: Place images in the FRONT (question), not the BACK (answer)
   - The question should ask about the diagram
   - The answer explains without repeating the image
4. **No tabs in content**: Use spaces or `<br>` instead of tab characters

# Card Quality Guidelines

{self._format_quality_guidelines()}

# Card Type Distribution

Generate approximately:
{dist_text}

# Example Cards

{self._format_example_cards()}

# Your Task

Generate exactly {target_cards} high-quality flashcards following these guidelines. Start with the required headers, then output one flashcard per line with tab-separated columns.

IMPORTANT:
- Do not include any explanatory text before or after the flashcards
- Start directly with the headers
- Use actual TAB characters to separate columns (not spaces)
- Each card should be on a single line (use <br> for line breaks within fields)
"""

        return prompt

    def validate_output(self, output_path: str) -> Dict[str, any]:
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


def generate_all_units(target_cards_per_unit: Dict[str, int] = None, config: Config = None):
    """
    Generate flashcards for all units.

    Args:
        target_cards_per_unit: Dictionary mapping unit names to target card counts
        config: Optional Config instance
    """
    if config is None:
        config = Config()

    if target_cards_per_unit is None:
        target_cards_per_unit = {
            'unit0_intro': 30,
            'unit1_fundamentals': 50,
            'unit2_concepts': 60,
            'unit3_core_topics': 70,
            'unit4_methods': 70,
            'unit5_techniques': 60,
            'unit6_advanced_topics': 60,
            'unit7_special_topics': 50,
            'unit8_applications': 50
        }

    generator = ClaudeCardGenerator(config=config)

    for unit_name, target_cards in target_cards_per_unit.items():
        try:
            output_path = generator.generate_flashcards(unit_name, target_cards)

            # Validate
            validation = generator.validate_output(output_path)

            print(f"\n{unit_name}:")
            print(f"  Generated: {output_path}")
            print(f"  Cards: {validation['card_count']}")
            print(f"  Valid: {validation['valid']}")

            if validation['warnings']:
                print(f"  Warnings: {len(validation['warnings'])}")

        except Exception as e:
            logger.error(f"Failed to generate flashcards for {unit_name}: {e}")
            print(f"\n{unit_name}: FAILED - {e}")


# Backward compatibility alias
FlashcardGenerator = ClaudeCardGenerator


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_all_units()
