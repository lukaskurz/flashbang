#!/usr/bin/env python3
"""
DEPRECATED: Use 'anki-gen generate' instead.

This script is maintained for backwards compatibility.

New usage:
    anki-gen generate --unit unit1_introduction
"""

import argparse
import sys
import os

# Print deprecation notice
print("=" * 80)
print("DEPRECATION NOTICE")
print("=" * 80)
print("This script (generate_cards.py) is deprecated.")
print("Please use the new unified CLI instead:")
print()
print("  anki-gen generate --unit <unit_name>")
print()
print("Calling new CLI now...")
print("=" * 80)
print()

from src.config import load_config
from src.utils import read_file


def generate_flashcards(unit_name: str):
    """
    Display markdown content and instructions for Claude Code to generate flashcards.

    Args:
        unit_name: Unit name (e.g., 'unit1_introduction')
    """
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False

    # Get unit info
    unit_info = config.get_unit_by_name(unit_name)
    if not unit_info:
        print(f"Error: Unit '{unit_name}' not found in config.yaml")
        print("\nAvailable units:")
        for pdf_filename, info in config.get_all_units().items():
            print(f"  - {info['unit_name']}")
        return False

    target_cards = unit_info.get('target_cards', 50)
    tags = unit_info.get('tags', [unit_name])
    base_tag = tags[0] if tags else unit_name

    # Load markdown file
    markdown_path = f"{config.markdown_dir}/{unit_name}.md"
    if not os.path.exists(markdown_path):
        print(f"Error: Markdown file not found: {markdown_path}")
        print("\nRun 'python extract_pdfs.py' first to extract PDFs to markdown.")
        return False

    try:
        markdown_content = read_file(markdown_path)
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return False

    # Calculate card distribution
    card_dist = config.card_distribution
    conceptual_count = int(target_cards * card_dist.get('conceptual', 0.40))
    worked_examples_count = int(target_cards * card_dist.get('worked_examples', 0.20))
    algorithm_count = int(target_cards * card_dist.get('algorithm', 0.20))
    pattern_count = int(target_cards * card_dist.get('pattern_recognition', 0.10))
    visual_count = int(target_cards * card_dist.get('visual', 0.10))

    # Output file path
    output_path = f"{config.anki_dir}/{unit_name}_anki.txt"

    # Display all information for Claude Code
    print("="*80)
    print(f"GENERATING ANKI FLASHCARDS FOR: {unit_name}")
    print("="*80)
    print()
    print(f"Target: {target_cards} flashcards")
    print(f"Base tag: {base_tag}")
    print(f"Output file: {output_path}")
    print(f"Markdown length: {len(markdown_content):,} characters")
    print()
    print("CARD DISTRIBUTION:")
    print(f"  - Conceptual Understanding: {conceptual_count} cards (~40%)")
    print(f"  - Simple Worked Examples: {worked_examples_count} cards (~20%)")
    print(f"  - Algorithm Comprehension: {algorithm_count} cards (~20%)")
    print(f"  - Pattern Recognition: {pattern_count} cards (~10%)")
    print(f"  - Visual/Diagram-Based: {visual_count} cards (~10%)")
    print()
    print("="*80)
    print("MARKDOWN CONTENT:")
    print("="*80)
    print()
    print(markdown_content)
    print()
    print("="*80)
    print("END OF MARKDOWN CONTENT")
    print("="*80)
    print()
    print()
    print("="*80)
    print("INSTRUCTIONS FOR CLAUDE CODE:")
    print("="*80)
    print()
    print(f"Please analyze the markdown content above and generate {target_cards} high-quality")
    print("Anki flashcards following these guidelines:")
    print()
    print("CARD REQUIREMENTS:")
    print("  1. Conceptual Understanding (40%): Why/how questions, test intuition")
    print("  2. Simple Worked Examples (20%): Tiny scenarios, mental math only")
    print("  3. Algorithm Comprehension (20%): Step analysis, key insights")
    print("  4. Pattern Recognition (10%): Identify reasoning patterns")
    print("  5. Visual/Diagram-Based (10%): Use extracted images when relevant")
    print()
    print("OUTPUT FORMAT:")
    print("  Tab-separated TSV with these exact headers:")
    print()
    print("  #separator:tab")
    print("  #html:true")
    print("  #tags column:3")
    print("  Front\tBack\tTags")
    print()
    print("FORMATTING GUIDELINES:")
    print("  - Front: Clear question or prompt (one line)")
    print("  - Back: HTML-formatted answer with:")
    print("    • <strong> for emphasis")
    print("    • <br> for line breaks (use <br><br> for paragraphs)")
    print("    • \\(...\\) for inline math (MathJax)")
    print("    • \\[...\\] for display math (MathJax)")
    print("    • <img src=\"../images/filename.png\" style=\"max-width:500px;\"> for diagrams")
    print(f"  - Tags: space-separated, hierarchical (start with '{base_tag}')")
    print("    Example: {base_tag} specific-concept sub-concept")
    print()
    print("QUALITY GUIDELINES:")
    print("  - Test understanding, not memorization")
    print("  - Use concrete examples")
    print("  - No complex calculations needed")
    print("  - Explain 'why' not just 'what'")
    print("  - One concept per card")
    print("  - Vary question types")
    print()
    print("EXAMPLE CARD:")
    print("  Front: Why is conditional independence crucial for Bayesian Networks?")
    print("  Back: It enables <strong>factorization of the joint distribution</strong>:<br><br>")
    print("        \\[P(X_1,...,X_n) = \\prod_{i=1}^{n} P(X_i | Parents(X_i))\\]<br><br>")
    print("        This reduces storage from \\(O(2^n)\\) to \\(O(n \\cdot 2^k)\\) where k is")
    print("        the maximum number of parents!")
    print(f"  Tags: {base_tag} conditional-independence complexity")
    print()
    print("="*80)
    print(f"PLEASE WRITE THE {target_cards} FLASHCARDS TO:")
    print(f"  {output_path}")
    print("="*80)
    print()
    print("Waiting for Claude Code to generate flashcards...")
    print()

    return True


def main():
    """Main entry point - calls new CLI."""
    parser = argparse.ArgumentParser(
        description="Generate Anki flashcards for a specific unit (Claude Code interaction)"
    )
    parser.add_argument(
        '--unit',
        required=True,
        help='Unit name (e.g., unit1_introduction, unit2_probability)'
    )

    args = parser.parse_args()

    # Use new CLI instead
    from src.cli.generate import generate_command

    try:
        success = generate_command(args.unit, show_images=False)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nFalling back to old implementation...")
        success = generate_flashcards(args.unit)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
