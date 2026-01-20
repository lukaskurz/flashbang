"""
Package command - Refactored from generate_apkg.py.
Generates .apkg Anki deck files with embedded images.
"""

import genanki
import logging
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

from src.config import Config
from src.tsv_parser import parse_anki_tsv
from src.image_extractor import prepare_card_for_apkg
from src.genanki_models import create_model
from src.utils import ensure_dir

console = Console()


def generate_apkg_for_unit(unit_name: str, config: Config) -> dict:
    """
    Generate .apkg file for a single unit.

    Args:
        unit_name: Name of the unit (e.g., 'unit3_bayesian_networks')
        config: Configuration object

    Returns:
        Dictionary with generation statistics

    Raises:
        FileNotFoundError: If .txt file doesn't exist
        ValueError: If parsing fails
    """
    logger = logging.getLogger(__name__)

    # Parse TSV file
    txt_path = Path(config.anki_dir) / f"{unit_name}_anki.txt"
    logger.info(f"Parsing {txt_path}")

    deck_data = parse_anki_tsv(str(txt_path), config)

    # Create deck with unique ID based on unit name
    deck_id = abs(hash(unit_name)) % (2 ** 31)
    deck = genanki.Deck(deck_id, deck_data['deck_name'])

    logger.info(f"Creating deck: {deck_data['deck_name']} (ID: {deck_id})")

    # Create model with subject name
    model_name = config.subject_name
    model = create_model(model_name)

    # Track all media files
    all_media = set()

    # Create notes
    for card in deck_data['cards']:
        # Process front and back for images
        front_html, front_media = prepare_card_for_apkg(card['front'], config.images_dir)
        back_html, back_media = prepare_card_for_apkg(card['back'], config.images_dir)

        all_media.update(front_media)
        all_media.update(back_media)

        # Create note
        tags_str = ' '.join(card['tags'])
        note = genanki.Note(
            model=model,
            fields=[front_html, back_html, tags_str],
            tags=card['tags']
        )
        deck.add_note(note)

    logger.info(f"Created {len(deck_data['cards'])} notes with {len(all_media)} unique images")

    # Create package with media
    package = genanki.Package(deck)
    package.media_files = list(all_media)

    # Ensure output directory exists
    ensure_dir(config.apkg_dir)

    # Write .apkg file
    output_path = Path(config.apkg_dir) / f"{unit_name}_anki.apkg"
    package.write_to_file(str(output_path))

    logger.info(f"Generated {output_path}")

    return {
        'unit': unit_name,
        'deck_name': deck_data['deck_name'],
        'cards': len(deck_data['cards']),
        'media': len(all_media),
        'output': output_path
    }


def package_command(unit=None, package_all=False):
    """
    Package flashcards into .apkg files.

    Args:
        unit: Specific unit to package
        package_all: Package all units
    """
    console.print(Panel.fit(
        "[bold cyan]Package Anki Decks (.apkg)[/bold cyan]",
        subtitle="anki-gen package"
    ))

    # Load configuration
    config = Config()

    if package_all:
        # Generate for all units
        console.print("[cyan]Generating .apkg files for all units...[/cyan]\n")

        all_units = config.get_all_units()
        stats_list = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Packaging units...", total=len(all_units))

            for pdf_filename, unit_info in all_units.items():
                unit_name = unit_info['unit_name']
                try:
                    stats = generate_apkg_for_unit(unit_name, config)
                    stats_list.append(stats)
                    console.print(f"[green]✓[/green] {stats['unit']}: {stats['cards']} cards, {stats['media']} images")
                except Exception as e:
                    console.print(f"[red]✗[/red] {unit_name}: FAILED - {e}")

                progress.advance(task)

        # Summary
        console.print()
        summary = Table(title="Packaging Summary", show_header=True, header_style="bold cyan")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Count", justify="right", style="green")

        total_cards = sum(s['cards'] for s in stats_list)
        total_media = sum(s['media'] for s in stats_list)

        summary.add_row("Decks Generated", str(len(stats_list)))
        summary.add_row("Total Cards", str(total_cards))
        summary.add_row("Total Images", str(total_media))

        console.print(summary)

    elif unit:
        # Generate for specific unit
        try:
            stats = generate_apkg_for_unit(unit, config)
            console.print(f"[green]✓ Generated {stats['output']}[/green]")

            info_table = Table(show_header=False, box=None)
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="green")

            info_table.add_row("Deck", stats['deck_name'])
            info_table.add_row("Cards", str(stats['cards']))
            info_table.add_row("Images", str(stats['media']))

            console.print(info_table)

        except Exception as e:
            console.print(f"[red]✗ FAILED: {e}[/red]")
            return False

    else:
        # No arguments provided
        console.print("[yellow]Please specify --unit <name> or --all[/yellow]")
        console.print("\nExamples:")
        console.print("  [green]anki-gen package --unit unit3_bayesian_networks[/green]")
        console.print("  [green]anki-gen package --all[/green]")
        return False

    console.print("\n[bold cyan]Next Step:[/bold cyan]")
    console.print("Import .apkg files into Anki Desktop: [dim]File → Import[/dim]")

    return True
