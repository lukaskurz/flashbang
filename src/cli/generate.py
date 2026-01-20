"""
Generate command - Refactored from generate_cards.py.
Displays markdown with image descriptions for Claude to generate flashcards.
"""

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from src.config import load_config
from src.utils import read_file

console = Console()


def generate_command(unit_name: str, show_images: bool = False):
    """
    Display markdown content and instructions for Claude Code to generate flashcards.

    Args:
        unit_name: Unit name (e.g., 'unit1_introduction')
        show_images: Display image descriptions in output
    """
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]✗ Error loading configuration: {e}[/red]")
        return False

    # Get unit info
    unit_info = config.get_unit_by_name(unit_name)
    if not unit_info:
        console.print(f"[red]✗ Unit '{unit_name}' not found in config.yaml[/red]")
        console.print("\n[cyan]Available units:[/cyan]")
        for pdf_filename, info in config.get_all_units().items():
            console.print(f"  [dim]- {info['unit_name']}[/dim]")
        return False

    target_cards = unit_info.get('target_cards', 50)
    tags = unit_info.get('tags', [unit_name])
    base_tag = tags[0] if tags else unit_name

    # Load markdown file
    markdown_path = f"{config.markdown_dir}/{unit_name}.md"
    if not os.path.exists(markdown_path):
        console.print(f"[red]✗ Markdown file not found: {markdown_path}[/red]")
        console.print("\n[yellow]Run 'anki-gen extract' first to extract PDFs to markdown.[/yellow]")
        return False

    try:
        markdown_content = read_file(markdown_path)
    except Exception as e:
        console.print(f"[red]✗ Error reading markdown file: {e}[/red]")
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

    # Display header
    console.print(Panel.fit(
        f"[bold cyan]GENERATING ANKI FLASHCARDS FOR: {unit_name}[/bold cyan]",
        subtitle=f"Target: {target_cards} flashcards"
    ))

    # Display configuration table
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")

    info_table.add_row("Base tag", base_tag)
    info_table.add_row("Output file", output_path)
    info_table.add_row("Markdown length", f"{len(markdown_content):,} characters")

    console.print(info_table)
    console.print()

    # Display card distribution
    dist_table = Table(title="Card Distribution", show_header=True, header_style="bold cyan")
    dist_table.add_column("Type", style="cyan")
    dist_table.add_column("Count", justify="right", style="green")
    dist_table.add_column("Percentage", justify="right", style="dim")

    dist_table.add_row("Conceptual Understanding", str(conceptual_count), "~40%")
    dist_table.add_row("Simple Worked Examples", str(worked_examples_count), "~20%")
    dist_table.add_row("Algorithm Comprehension", str(algorithm_count), "~20%")
    dist_table.add_row("Pattern Recognition", str(pattern_count), "~10%")
    dist_table.add_row("Visual/Diagram-Based", str(visual_count), "~10%")

    console.print(dist_table)
    console.print()

    # Show image descriptions if available
    if show_images:
        from src.metadata.storage import MetadataStorage
        metadata_store = MetadataStorage()
        if metadata_store.load():
            unit_images = [img for img in metadata_store.get_all_images() if img['unit'] == unit_name]
            if unit_images:
                console.print(f"[cyan]Available images for {unit_name}: {len(unit_images)}[/cyan]")
                for img in unit_images[:5]:  # Show first 5
                    desc = img.get('description', 'No description')
                    console.print(f"  [dim]• {img['filename']}: {desc[:80]}...[/dim]")
                if len(unit_images) > 5:
                    console.print(f"  [dim]... and {len(unit_images) - 5} more[/dim]")
                console.print()

    # Display markdown content
    console.print("="*80)
    console.print("[bold cyan]MARKDOWN CONTENT:[/bold cyan]")
    console.print("="*80)
    console.print()
    print(markdown_content)  # Use print to avoid Rich formatting
    console.print()
    console.print("="*80)
    console.print("[bold cyan]END OF MARKDOWN CONTENT[/bold cyan]")
    console.print("="*80)
    console.print()

    # Display instructions for Claude Code
    console.print(Panel.fit(
        "[bold yellow]INSTRUCTIONS FOR CLAUDE CODE[/bold yellow]",
        subtitle="Please follow these guidelines"
    ))
    console.print()

    instructions = f"""
Please analyze the markdown content above and generate {target_cards} high-quality
Anki flashcards following these guidelines:

[bold cyan]CARD REQUIREMENTS:[/bold cyan]
  1. Conceptual Understanding (40%): Why/how questions, test intuition
  2. Simple Worked Examples (20%): Tiny scenarios, mental math only
  3. Algorithm Comprehension (20%): Step analysis, key insights
  4. Pattern Recognition (10%): Identify reasoning patterns
  5. Visual/Diagram-Based (10%): Use extracted images when relevant

[bold cyan]OUTPUT FORMAT:[/bold cyan]
  Tab-separated TSV with these exact headers:

  #separator:tab
  #html:true
  #tags column:3
  Front\tBack\tTags

[bold cyan]FORMATTING GUIDELINES:[/bold cyan]
  - Front: Clear question or prompt (one line)
  - Back: HTML-formatted answer with:
    • <strong> for emphasis
    • <br> for line breaks (use <br><br> for paragraphs)
    • \\(...\\) for inline math (MathJax)
    • \\[...\\] for display math (MathJax)
    • <img src="../images/filename.png" style="max-width:500px;"> for diagrams
  - Tags: space-separated, hierarchical (start with '{base_tag}')
    Example: {base_tag} specific-concept sub-concept

[bold cyan]QUALITY GUIDELINES:[/bold cyan]
  - Test understanding, not memorization
  - Use concrete examples
  - No complex calculations needed
  - Explain 'why' not just 'what'
  - One concept per card
  - Vary question types

[bold cyan]EXAMPLE CARD:[/bold cyan]
  Front: Why is conditional independence crucial for Bayesian Networks?
  Back: It enables <strong>factorization of the joint distribution</strong>:<br><br>
        \\[P(X_1,...,X_n) = \\prod_{{i=1}}^{{n}} P(X_i | Parents(X_i))\\]<br><br>
        This reduces storage from \\(O(2^n)\\) to \\(O(n \\cdot 2^k)\\) where k is
        the maximum number of parents!
  Tags: {base_tag} conditional-independence complexity
"""

    console.print(Markdown(instructions))
    console.print()

    console.print(Panel.fit(
        f"[bold green]PLEASE WRITE THE {target_cards} FLASHCARDS TO:[/bold green]\n{output_path}",
        border_style="green"
    ))
    console.print()
    console.print("[dim]Waiting for Claude Code to generate flashcards...[/dim]")
    console.print()

    return True
