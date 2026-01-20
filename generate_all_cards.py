#!/usr/bin/env python3
"""
Generate Anki flashcards for ALL units automatically.

This script prepares all unit information and displays instructions
for Claude Code to spawn agents for each unit.

Usage:
    python generate_all_cards.py
"""

import sys
import os

from src.config import load_config
from src.utils import ensure_dir


def prepare_agent_tasks():
    """
    Prepare task information for Claude Code to spawn agents for all units.

    Displays all unit information and instructions for Claude Code.
    """
    print("="*80)
    print("AUTOMATED ANKI FLASHCARD GENERATION")
    print("="*80)
    print()

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False

    # Ensure output directory exists
    ensure_dir(config.anki_dir)

    # Get all units
    units = config.get_all_units()
    total_units = len(units)

    print(f"Found {total_units} units to process")
    print()
    print("="*80)
    print("UNIT INFORMATION")
    print("="*80)
    print()

    # Prepare information for each unit
    unit_tasks = []

    for idx, (pdf_filename, unit_info) in enumerate(units.items(), 1):
        unit_name = unit_info['unit_name']
        target_cards = unit_info.get('target_cards', 50)
        tags = unit_info.get('tags', [unit_name])
        base_tag = tags[0] if tags else unit_name

        markdown_path = f"{config.markdown_dir}/{unit_name}.md"
        output_path = f"{config.anki_dir}/{unit_name}_anki.txt"

        if not os.path.exists(markdown_path):
            print(f"[{idx}/{total_units}] {unit_name}: ✗ Markdown not found at {markdown_path}")
            continue

        # Calculate card distribution
        card_dist = config.card_distribution
        conceptual = int(target_cards * card_dist.get('conceptual', 0.40))
        examples = int(target_cards * card_dist.get('worked_examples', 0.20))
        algorithm = int(target_cards * card_dist.get('algorithm', 0.20))
        pattern = int(target_cards * card_dist.get('pattern_recognition', 0.10))
        visual = int(target_cards * card_dist.get('visual', 0.10))

        unit_task = {
            'index': idx,
            'unit_name': unit_name,
            'target_cards': target_cards,
            'base_tag': base_tag,
            'markdown_path': markdown_path,
            'output_path': output_path,
            'distribution': {
                'conceptual': conceptual,
                'examples': examples,
                'algorithm': algorithm,
                'pattern': pattern,
                'visual': visual
            }
        }

        unit_tasks.append(unit_task)

        print(f"[{idx}/{total_units}] {unit_name}")
        print(f"  Markdown: {markdown_path}")
        print(f"  Output: {output_path}")
        print(f"  Target: {target_cards} cards")
        print(f"    • Conceptual Understanding: {conceptual} cards")
        print(f"    • Simple Worked Examples: {examples} cards")
        print(f"    • Algorithm Comprehension: {algorithm} cards")
        print(f"    • Pattern Recognition: {pattern} cards")
        print(f"    • Visual/Diagram-Based: {visual} cards")
        print(f"  Base tag: {base_tag}")
        print()

    print("="*80)
    print("FLASHCARD GENERATION GUIDELINES")
    print("="*80)
    print()
    print("Each agent should generate flashcards following these requirements:")
    print()
    print("CARD QUALITY:")
    print("  • Test understanding, not memorization")
    print("  • Use concrete examples with simple calculations")
    print("  • Explain 'why' not just 'what'")
    print("  • One concept per card")
    print("  • Vary question types")
    print()
    print("OUTPUT FORMAT (Tab-separated TSV):")
    print("  #separator:tab")
    print("  #html:true")
    print("  #tags column:3")
    print("  Front\\tBack\\tTags")
    print()
    print("FORMATTING:")
    print("  • Front: Clear question or prompt (one line)")
    print("  • Back: HTML-formatted answer with:")
    print("    - <strong> for emphasis")
    print("    - <br> for line breaks (use <br><br> for paragraphs)")
    print("    - \\(...\\) for inline math (MathJax)")
    print("    - \\[...\\] for display math (MathJax)")
    print("    - <img src=\\\"../images/filename.png\\\" style=\\\"max-width:500px;\\\"> for diagrams")
    print("  • Tags: space-separated, hierarchical (start with base tag)")
    print()
    print("EXAMPLE CARD:")
    print("  Front: Why is conditional independence crucial for Bayesian Networks?")
    print("  Back: It enables <strong>factorization of the joint distribution</strong>:<br><br>")
    print("        \\[P(X_1,...,X_n) = \\prod_{i=1}^{n} P(X_i | Parents(X_i))\\]<br><br>")
    print("        This reduces storage from \\(O(2^n)\\) to \\(O(n \\cdot 2^k)\\) where k is")
    print("        the maximum number of parents!")
    print("  Tags: unit3 conditional-independence complexity")
    print()
    print("="*80)
    print(f"INSTRUCTIONS FOR CLAUDE CODE")
    print("="*80)
    print()
    print(f"Please spawn {len(unit_tasks)} Task agents (subagent_type='general-purpose')")
    print("to generate Anki flashcards for all units listed above.")
    print()
    print("For each unit, create an agent with a task prompt like:")
    print()
    print("  '''")
    print("  Generate Anki flashcards for [unit_name].")
    print()
    print("  1. Read the markdown file at: [markdown_path]")
    print("  2. Generate [target_cards] flashcards following the guidelines:")
    print("     - [distribution details]")
    print("  3. Write the output in TSV format to: [output_path]")
    print()
    print("  Follow all formatting guidelines for MathJax, HTML, images, and tags.")
    print("  '''")
    print()
    print("="*80)
    print(f"READY TO SPAWN {len(unit_tasks)} AGENTS")
    print("="*80)
    print()
    print("Waiting for Claude Code to spawn Task agents...")
    print()

    # Return unit tasks for potential programmatic use
    return unit_tasks


def main():
    """Main entry point."""
    result = prepare_agent_tasks()

    if result is False:
        sys.exit(1)

    print("Script complete. Claude Code should now spawn agents to generate flashcards.")
    sys.exit(0)


if __name__ == '__main__':
    main()
