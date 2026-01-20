"""
List command - Display available units and their status.
"""

import os
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config import load_config

console = Console()


def list_command(detailed=False, stats=False):
    """
    List available units and their status.

    Args:
        detailed: Show detailed unit information
        stats: Show statistics
    """
    console.print(Panel.fit(
        "[bold cyan]Available Units[/bold cyan]",
        subtitle="flashbang list"
    ))

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]✗ Error loading configuration: {e}[/red]")
        return False

    all_units = config.get_all_units()

    if not all_units:
        console.print("[yellow]No units found in config.yaml[/yellow]")
        return False

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("Unit Name", style="cyan")
    table.add_column("PDF File", style="dim")
    table.add_column("Target", justify="right", style="green")

    if detailed:
        table.add_column("Markdown", justify="center", style="yellow")
        table.add_column("TSV", justify="center", style="yellow")
        table.add_column("APKG", justify="center", style="yellow")

    if stats:
        table.add_column("Tags", style="blue")

    # Populate table
    for idx, (pdf_filename, unit_info) in enumerate(all_units.items(), 1):
        unit_name = unit_info['unit_name']
        target_cards = unit_info.get('target_cards', 50)
        source = unit_info.get('source', 'configured')

        # Add source indicator to unit name
        if source == 'auto-discovered':
            unit_name_display = f"{unit_name} [dim](auto)[/dim]"
        elif source == 'configured-only':
            unit_name_display = f"{unit_name} [yellow](config only - PDF missing)[/yellow]"
        else:
            unit_name_display = unit_name

        row = [
            str(idx),
            unit_name_display,
            pdf_filename,
            str(target_cards)
        ]

        if detailed:
            # Check file existence
            md_exists = os.path.exists(f"{config.markdown_dir}/{unit_name}.md")
            tsv_exists = os.path.exists(f"{config.anki_dir}/{unit_name}_anki.txt")
            apkg_exists = os.path.exists(f"{config.apkg_dir}/{unit_name}_anki.apkg")

            row.extend([
                "[green]✓[/green]" if md_exists else "[red]✗[/red]",
                "[green]✓[/green]" if tsv_exists else "[red]✗[/red]",
                "[green]✓[/green]" if apkg_exists else "[red]✗[/red]"
            ])

        if stats:
            tags = unit_info.get('tags', [])
            row.append(", ".join(tags[:3]))

        table.add_row(*row)

    console.print(table)

    # Show summary statistics
    if stats:
        console.print()
        total_cards = sum(u.get('target_cards', 50) for u in all_units.values())

        summary = Table(show_header=False, box=None)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", justify="right", style="green")

        summary.add_row("Total Units", str(len(all_units)))
        summary.add_row("Total Target Cards", str(total_cards))

        console.print(summary)

    # Show next steps
    if detailed:
        console.print("\n[bold cyan]Legend:[/bold cyan]")
        console.print("  Markdown: Extracted from PDF")
        console.print("  TSV: Flashcards generated")
        console.print("  APKG: Packaged for Anki")

    console.print("\n[bold cyan]Common Commands:[/bold cyan]")
    console.print("  [green]flashbang extract[/green] - Extract PDFs to markdown")
    console.print("  [green]flashbang generate --unit <name>[/green] - Generate flashcards")
    console.print("  [green]flashbang package --unit <name>[/green] - Package into .apkg")

    return True
