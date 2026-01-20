"""
Generate command - Generate flashcards using Claude or Ollama.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.config import load_config

console = Console()


def generate_command(unit_name: str, show_images: bool = False, provider: str = None):
    """
    Generate flashcards for a unit using Claude or Ollama.

    Args:
        unit_name: Unit name (e.g., 'unit1_introduction')
        show_images: Display image descriptions in output
        provider: Override provider ('claude' or 'ollama')
    """
    from src.flashcards.factory import create_card_generator

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

    # Check if markdown exists
    markdown_path = f"{config.markdown_dir}/{unit_name}.md"
    if not os.path.exists(markdown_path):
        console.print(f"[red]✗ Markdown file not found: {markdown_path}[/red]")
        console.print("\n[yellow]Run 'anki-gen extract' first to extract PDFs to markdown.[/yellow]")
        return False

    # Display header
    provider_name = provider or config.generation_provider
    console.print(Panel.fit(
        f"[bold cyan]GENERATING FLASHCARDS: {unit_name}[/bold cyan]",
        subtitle=f"Provider: {provider_name} | Target: {target_cards} cards"
    ))

    try:
        # Create generator
        generator = create_card_generator(config, provider=provider)

        # Show provider info
        info = generator.get_provider_info()
        console.print(f"[cyan]Using:[/cyan] {info['provider']} ({info['model']})")
        console.print()

        # Show image info if requested
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

        # Generate flashcards
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                "[cyan]Generating flashcards...",
                total=None
            )

            output_path = generator.generate_flashcards(
                unit_name=unit_name,
                target_cards=target_cards,
                output_dir=config.anki_dir
            )

        # Validate output
        validation = generator.validate_output(output_path)

        # Display results
        console.print()
        if validation['valid']:
            console.print(f"[green]✓ Generated {validation['card_count']} cards[/green]")
            console.print(f"[green]✓ Saved to {output_path}[/green]")
        else:
            console.print(f"[yellow]⚠ Generated but has issues:[/yellow]")
            for error in validation['errors']:
                console.print(f"  [red]✗ {error}[/red]")
            for warning in validation['warnings'][:5]:  # Show first 5
                console.print(f"  [yellow]⚠ {warning}[/yellow]")

        return True

    except Exception as e:
        console.print(f"[red]✗ Generation failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False
