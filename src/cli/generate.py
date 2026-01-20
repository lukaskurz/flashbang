"""
Generate command - Generate flashcards using Claude or Ollama.
"""

import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from src.config import load_config

console = Console()


def generate_command(unit_name: str = None, show_images: bool = False, provider: str = None):
    """
    Generate flashcards for a unit using Claude or Ollama.

    Args:
        unit_name: Unit name (e.g., 'unit1_introduction'), or None to generate all units
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

    # If no unit specified, generate all units
    if unit_name is None:
        all_units = config.get_all_units()
        if not all_units:
            console.print("[red]✗ No units found in config.yaml[/red]")
            return False

        console.print(f"[cyan]Generating flashcards for all {len(all_units)} units...[/cyan]\n")

        results = []
        for pdf_filename, unit_info in all_units.items():
            success = _generate_single_unit(
                config,
                unit_info['unit_name'],
                show_images,
                provider
            )
            results.append((unit_info['unit_name'], success))
            console.print()  # Add spacing between units

        # Display summary
        console.print(Panel.fit(
            "[bold cyan]GENERATION SUMMARY[/bold cyan]",
        ))

        success_count = sum(1 for _, success in results if success)
        total_count = len(results)

        for unit, success in results:
            status = "[green]✓[/green]" if success else "[red]✗[/red]"
            console.print(f"{status} {unit}")

        console.print(f"\n[cyan]Completed: {success_count}/{total_count} units[/cyan]")
        return success_count == total_count

    # Get unit info
    unit_info = config.get_unit_by_name(unit_name)
    if not unit_info:
        console.print(f"[red]✗ Unit '{unit_name}' not found in config.yaml[/red]")
        console.print("\n[cyan]Available units:[/cyan]")
        for pdf_filename, info in config.get_all_units().items():
            console.print(f"  [dim]- {info['unit_name']}[/dim]")
        return False

    return _generate_single_unit(config, unit_name, show_images, provider)


def _generate_single_unit(config, unit_name: str, show_images: bool = False, provider: str = None) -> bool:
    """
    Generate flashcards for a single unit.

    Args:
        config: Config object
        unit_name: Unit name (e.g., 'unit1_introduction')
        show_images: Display image descriptions in output
        provider: Override provider ('claude' or 'ollama')

    Returns:
        True if successful, False otherwise
    """
    from src.flashcards.factory import create_card_generator

    # Get unit info
    unit_info = config.get_unit_by_name(unit_name)
    if not unit_info:
        console.print(f"[red]✗ Unit '{unit_name}' not found[/red]")
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
    console.print(Panel(
        f"[bold cyan]GENERATING FLASHCARDS: {unit_name}[/bold cyan]\n"
        f"[dim]Provider: {provider_name} | Target: {target_cards} cards[/dim]"
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

        # Generate flashcards with progress tracking
        # Track progress state
        progress_state = {
            'lines_generated': 0,
            'start_time': time.time(),
            'buffer': ''
        }

        def create_progress_display():
            """Create a rich display of current progress."""
            elapsed = time.time() - progress_state['start_time']
            lines = progress_state['lines_generated']

            # Estimate cards (each card is one line after headers)
            cards_estimate = max(0, lines - 4)  # Subtract 4 header lines

            display = Text()
            display.append("Generating flashcards", style="bold cyan")
            display.append(f"\n  Elapsed: {elapsed:.1f}s", style="dim")
            display.append(f"\n  Lines: {lines}", style="yellow")
            if cards_estimate > 0:
                display.append(f" (~{cards_estimate} cards)", style="green")
            display.append(f"\n  Target: {target_cards} cards", style="dim")

            return display

        def progress_callback(chunk: str):
            """Update progress as chunks arrive."""
            progress_state['buffer'] += chunk
            # Count complete lines
            progress_state['lines_generated'] = progress_state['buffer'].count('\n')

        with Live(create_progress_display(), console=console, refresh_per_second=4) as live:
            def update_callback(chunk: str):
                progress_callback(chunk)
                live.update(create_progress_display())

            output_path = generator.generate_flashcards(
                unit_name=unit_name,
                target_cards=target_cards,
                output_dir=config.anki_dir,
                progress_callback=update_callback
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
