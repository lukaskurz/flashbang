"""
Anki flashcard generator using Ollama.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from src.config import Config
from src.flashcards.base import CardGenerationProvider
from src.ollama.client import OllamaClient
from src.pdf_processor import PDFProcessor

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

    def get_pdf_page_count(self, unit_name: str) -> int:
        """
        Get the page count for a unit's PDF.

        Args:
            unit_name: Unit name (e.g., 'unit_2')

        Returns:
            Number of pages in the PDF, or 0 if PDF not found
        """
        # Find the PDF file for this unit
        units = self.config.get_all_units()
        pdf_file = None

        for pdf_filename, unit_info in units.items():
            if unit_info.get('unit_name') == unit_name:
                pdf_file = pdf_filename
                break

        if not pdf_file:
            logger.warning(f"No PDF found for unit: {unit_name}")
            return 0

        # Get the PDF path
        pdf_path = Path('pdfs') / pdf_file

        if not pdf_path.exists():
            logger.warning(f"PDF file not found: {pdf_path}")
            return 0

        # Get page count using PDFProcessor
        try:
            with PDFProcessor(str(pdf_path), unit_name) as processor:
                page_count = processor.get_page_count()
                logger.info(f"PDF {pdf_file} has {page_count} pages")
                return page_count
        except Exception as e:
            logger.error(f"Failed to get page count for {pdf_file}: {e}")
            return 0

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

    def _check_and_truncate_for_context(
        self,
        markdown_content: str,
        target_cards: int,
        images: List[Dict]
    ) -> str:
        """
        Check if content fits within model's context window and truncate if needed.

        Estimates token usage and truncates markdown content if necessary to leave
        room for the prompt template and generated output.

        Args:
            markdown_content: Full markdown content
            target_cards: Target number of cards to generate
            images: Image metadata list

        Returns:
            Possibly truncated markdown content
        """
        # Get model's context length
        context_length = self.client.get_context_length()
        logger.info(f"Model context length: {context_length} tokens")

        # Estimate token budgets
        # Prompt template overhead (without content): ~2000 tokens
        prompt_overhead = 2000

        # Image descriptions: ~50 tokens each
        image_tokens = len(images) * 50

        # Output estimate: ~100 tokens per card (front + back + tags + formatting)
        # Add 20% buffer for safety
        output_tokens = int(target_cards * 100 * 1.2)

        # Available tokens for markdown content
        available_for_content = context_length - prompt_overhead - image_tokens - output_tokens

        # Estimate current content tokens
        content_tokens = self.client.estimate_tokens(markdown_content)

        logger.info(
            f"Token budget: context={context_length}, "
            f"overhead={prompt_overhead}, images={image_tokens}, "
            f"output_reserve={output_tokens}, "
            f"available_for_content={available_for_content}, "
            f"content_estimate={content_tokens}"
        )

        if content_tokens <= available_for_content:
            logger.info("Content fits within context window")
            return markdown_content

        # Need to truncate
        # Calculate what percentage of content we can keep
        keep_ratio = available_for_content / content_tokens
        # Add safety margin
        keep_ratio = max(0.5, keep_ratio * 0.9)  # Keep at least 50%

        target_chars = int(len(markdown_content) * keep_ratio)

        logger.warning(
            f"Content exceeds context window! "
            f"Truncating to ~{int(keep_ratio * 100)}% ({target_chars} chars). "
            f"Consider processing smaller units or using a model with larger context."
        )

        # Truncate intelligently - try to end at a section boundary
        truncated = markdown_content[:target_chars]

        # Find last complete section (##)
        last_section = truncated.rfind('\n## ')
        if last_section > target_chars * 0.7:  # Only use if we keep at least 70%
            truncated = truncated[:last_section]

        # Add truncation notice
        truncated += "\n\n[... content truncated due to context length limits ...]\n"

        logger.info(f"Truncated content from {len(markdown_content)} to {len(truncated)} chars")
        return truncated

    def generate_flashcards(
        self,
        unit_name: str,
        target_cards: int = 60,
        output_dir: str = "outputs",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Generate Anki flashcards for a unit using Ollama.

        Args:
            unit_name: Unit name (e.g., 'unit3_core_topics')
            target_cards: Target number of flashcards to generate
            output_dir: Output directory for .txt file
            progress_callback: Optional callback function(chunk: str) for progress updates

        Returns:
            Path to generated .txt file
        """
        logger.info(f"Generating flashcards for {unit_name} using Ollama")

        # Load content
        markdown_content = self.load_markdown(unit_name)
        images = self.load_image_metadata(unit_name)

        # Calculate dynamic limit based on page count (1.5 cards per page)
        page_count = self.get_pdf_page_count(unit_name)
        if page_count > 0:
            effective_target = int(page_count * 1.5)
            logger.info(
                f"PDF has {page_count} pages. "
                f"Target: {effective_target} cards (1.5 per page). "
                f"Config requested: {target_cards}"
            )
        else:
            effective_target = target_cards
            logger.warning(
                f"Could not determine page count, using config target: {target_cards}"
            )

        # Check context window and potentially truncate content
        markdown_content = self._check_and_truncate_for_context(
            markdown_content, 
            effective_target,
            images
        )

        # Create prompt
        prompt = self._create_generation_prompt(
            markdown_content,
            images,
            effective_target
        )

        # Generate using Ollama
        logger.info(f"Calling Ollama ({self.client.model}) to generate ~{effective_target} flashcards...")

        # Create a wrapper callback that stops generation when target is reached
        accumulated_content = []
        card_count = [0]  # Use list to allow modification in nested function
        # Add buffer: stop when we have target + 2 cards (to ensure we reach target)
        stop_threshold = effective_target + 2

        def counting_callback(chunk: str) -> None:
            """Callback that counts cards."""
            accumulated_content.append(chunk)
            full_text = ''.join(accumulated_content)

            # Count lines that look like flashcards (contain tabs)
            lines = full_text.split('\n')
            card_count[0] = sum(1 for line in lines if line.count('\t') >= 2)

            # Call the original callback for progress updates
            if progress_callback:
                progress_callback(chunk)

        def should_stop(full_text: str) -> bool:
            """Check if we have enough cards to stop generation."""
            lines = full_text.split('\n')
            current_count = sum(1 for line in lines if line.count('\t') >= 2)
            if current_count >= stop_threshold:
                logger.info(f"Generated {current_count} cards, stopping (target: {effective_target})")
                return True
            return False

        # Use streaming for early stopping capability
        use_streaming = True

        # Prepare output path
        output_path = Path(output_dir) / f"{unit_name}_anki.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        flashcard_content = None
        interrupted = False

        try:
            flashcard_content = self.client.generate_text(
                prompt=prompt,
                temperature=self.temperature,
                stream=use_streaming,
                progress_callback=counting_callback if use_streaming else None,
                stop_condition=should_stop
            )
        except KeyboardInterrupt:
            interrupted = True
            logger.info("Generation interrupted by user")

            # Use accumulated content if available (streaming mode)
            if accumulated_content:
                flashcard_content = ''.join(accumulated_content)
                logger.info(f"Saving {card_count[0]} partially generated cards...")
            else:
                logger.warning("No content generated before interruption")
                raise

        if not flashcard_content:
            raise RuntimeError("Ollama failed to generate flashcards")

        # Truncate to effective_target cards if we exceeded it
        flashcard_content = self._truncate_to_target(flashcard_content, effective_target)

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(flashcard_content)

        if interrupted:
            logger.info(f"Saved partial results to {output_path}")
        else:
            logger.info(f"Saved flashcards to {output_path}")

        return str(output_path)

    def _truncate_to_target(self, content: str, target_cards: int) -> str:
        """
        Truncate flashcard content to target number of cards.

        Args:
            content: Full flashcard content
            target_cards: Maximum number of cards to keep

        Returns:
            Truncated content with exactly target_cards or fewer
        """
        lines = content.split('\n')

        # Find header lines (first 4 lines)
        header_lines = []
        card_lines = []
        in_headers = True

        for line in lines:
            if in_headers:
                header_lines.append(line)
                # After "Front\tBack\tTags" line, we're done with headers
                if line.startswith('Front\tBack\tTags'):
                    in_headers = False
            else:
                # Only count lines with proper tab separation as cards
                if line.strip() and line.count('\t') >= 2:
                    card_lines.append(line)

        # Truncate to target
        if len(card_lines) > target_cards:
            logger.info(f"Truncating from {len(card_lines)} cards to {target_cards}")
            card_lines = card_lines[:target_cards]
        else:
            logger.info(f"Generated {len(card_lines)} cards (target: {target_cards})")

        # Reconstruct content
        return '\n'.join(header_lines + card_lines) + '\n'

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

    def get_context_usage_report(self, unit_name: str, target_cards: int = 60) -> Dict[str, Any]:
        """
        Get a report of estimated context window usage for a unit.

        Useful for debugging why generation might fail or produce fewer cards.

        Args:
            unit_name: Unit name to analyze
            target_cards: Target number of cards

        Returns:
            Dictionary with context usage analysis
        """
        markdown_content = self.load_markdown(unit_name)
        images = self.load_image_metadata(unit_name)

        context_length = self.client.get_context_length()

        # Estimate tokens
        prompt_overhead = 2000
        image_tokens = len(images) * 50
        output_tokens = int(target_cards * 100 * 1.2)
        content_tokens = self.client.estimate_tokens(markdown_content)

        total_estimated = prompt_overhead + image_tokens + content_tokens + output_tokens
        available_for_content = context_length - prompt_overhead - image_tokens - output_tokens

        fits = content_tokens <= available_for_content
        overflow = max(0, total_estimated - context_length)
        utilization = (total_estimated / context_length) * 100

        return {
            'unit_name': unit_name,
            'model': self.client.model,
            'context_length': context_length,
            'estimated_tokens': {
                'prompt_overhead': prompt_overhead,
                'image_metadata': image_tokens,
                'markdown_content': content_tokens,
                'output_reserve': output_tokens,
                'total': total_estimated
            },
            'available_for_content': available_for_content,
            'content_fits': fits,
            'overflow_tokens': overflow,
            'utilization_percent': round(utilization, 1),
            'recommendation': (
                "Content fits within context window" if fits else
                f"Content too large! Reduce by ~{overflow} tokens or use a larger context model"
            ),
            'content_length_chars': len(markdown_content),
            'image_count': len(images)
        }
