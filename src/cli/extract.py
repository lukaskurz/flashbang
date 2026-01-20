"""
Extract command - Refactored from extract_pdfs.py with Ollama integration.
"""

import sys
import time
import logging
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

from src.config import load_config
from src.pdf_processor import PDFProcessor
from src.markdown_generator import MarkdownGenerator
from src import utils

console = Console()


def extract_command(unit_filter=None, no_images=False, no_describe=False):
    """
    Extract PDFs to markdown with optional image descriptions.

    Args:
        unit_filter: Extract specific unit only (e.g., 'unit1_introduction')
        no_images: Skip image extraction
        no_describe: Skip Ollama image descriptions
    """
    start_time = time.time()

    # Setup logging
    logger = utils.setup_logging()

    console.print(Panel.fit(
        "[bold cyan]PDF Extraction to Markdown[/bold cyan]",
        subtitle="flashbang extract"
    ))

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]✗ Failed to load configuration: {e}[/red]")
        return False

    # Ensure output directories exist
    utils.ensure_dir(config.markdown_dir)
    utils.ensure_dir(config.images_dir)

    # Get units to process
    all_units = config.get_all_units()
    if unit_filter:
        # Filter by unit name
        units = {k: v for k, v in all_units.items() if v['unit_name'] == unit_filter}
        if not units:
            console.print(f"[red]✗ Unit '{unit_filter}' not found in config[/red]")
            return False
    else:
        units = all_units

    total_units = len(units)
    console.print(f"[cyan]Found {total_units} PDF(s) to process[/cyan]\n")

    # Check Ollama availability if descriptions requested
    ollama_available = False
    if not no_describe and not no_images:
        from src.ollama.client import OllamaClient
        client = OllamaClient()
        ollama_available = client.check_availability()

        if ollama_available:
            console.print("[green]✓ Ollama detected - will generate image descriptions[/green]")
        else:
            console.print("[yellow]⚠ Ollama not available - skipping image descriptions[/yellow]")
            console.print("[dim]  To enable: 1) Install Ollama, 2) Run 'ollama pull ministral-3:8b', 3) Start 'ollama serve'[/dim]")

    # Statistics tracking
    stats = {
        'total_pdfs': 0,
        'successful_pdfs': 0,
        'failed_pdfs': 0,
        'total_images': 0,
        'described_images': 0,
        'errors': []
    }

    # Initialize metadata storage
    from src.metadata.storage import MetadataStorage
    metadata_store = MetadataStorage()

    # Process each PDF with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        task = progress.add_task("[cyan]Processing PDFs...", total=total_units)

        for pdf_filename, unit_info in units.items():
            unit_name = unit_info['unit_name']

            progress.update(task, description=f"[cyan]Processing {unit_name}...")

            stats['total_pdfs'] += 1

            # Paths
            pdf_path = f"pdfs/{pdf_filename}"
            markdown_path = f"{config.markdown_dir}/{unit_name}.md"

            try:
                # Extract PDF content
                with PDFProcessor(pdf_path, unit_name) as processor:
                    # Extract text
                    pages_data = processor.extract_text_by_page()
                    logger.info(f"{unit_name}: Extracted {len(pages_data)} pages")

                    # Extract images (if configured)
                    images = []
                    if not no_images and config.extract_images:
                        images = processor.extract_images(
                            output_dir=config.images_dir,
                            min_size=config.min_image_size
                        )
                        logger.info(f"{unit_name}: Extracted {len(images)} images")
                        stats['total_images'] += len(images)

                        # Add to metadata store
                        metadata_store.add_images(images, unit_name)

                # Generate markdown
                md_gen = MarkdownGenerator(pages_data, images, unit_name)
                markdown = md_gen.generate_markdown()

                # Save markdown
                utils.save_file(markdown_path, markdown)
                logger.info(f"{unit_name}: Saved markdown ({len(markdown)} chars)")

                stats['successful_pdfs'] += 1

            except Exception as e:
                logger.error(f"{unit_name}: Failed - {e}")
                stats['failed_pdfs'] += 1
                stats['errors'].append(f"{pdf_filename}: {str(e)}")

            progress.advance(task)

    # Generate image descriptions with Ollama
    if ollama_available and not no_describe and stats['total_images'] > 0:
        console.print("\n[cyan]Generating image descriptions with Ollama...[/cyan]")

        from src.ollama.vision import describe_images_batch

        try:
            described_count = describe_images_batch(
                metadata_store,
                console=console,
                progress=True
            )
            stats['described_images'] = described_count
            console.print(f"[green]✓ Generated {described_count} descriptions[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Image description failed: {e}[/yellow]")

    # Save metadata
    if stats['total_images'] > 0:
        metadata_store.save()
        console.print(f"[green]✓ Saved metadata to {metadata_store.metadata_file}[/green]")

    # Final summary
    elapsed = time.time() - start_time

    console.print("\n" + "="*60)
    summary = Table(title="Extraction Summary", show_header=True, header_style="bold cyan")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Count", justify="right", style="green")

    summary.add_row("PDFs Processed", str(stats['successful_pdfs']))
    summary.add_row("Images Extracted", str(stats['total_images']))
    summary.add_row("Images Described", str(stats['described_images']))
    summary.add_row("Time Elapsed", f"{elapsed:.2f}s")

    console.print(summary)

    if stats['errors']:
        console.print(f"\n[yellow]⚠ Errors encountered: {len(stats['errors'])}[/yellow]")
        for error in stats['errors']:
            console.print(f"  [dim]- {error}[/dim]")

    # Next steps
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. Review markdown files: [dim]outputs/markdown/[/dim]")
    console.print("2. Check images: [dim]outputs/images/[/dim]")
    if stats['described_images'] > 0:
        console.print("3. View descriptions: [dim]outputs/metadata/image_descriptions.json[/dim]")
    console.print("4. Generate flashcards: [green]flashbang generate --unit <name>[/green]")
    console.print("="*60 + "\n")

    return stats['failed_pdfs'] == 0
