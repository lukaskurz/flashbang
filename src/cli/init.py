"""
Init command - Initialize configuration for a new subject.
"""

import os
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def init_command():
    """Initialize configuration for a new subject."""
    console.print(Panel.fit(
        "[bold cyan]Initialize New Subject[/bold cyan]",
        subtitle="flashbang init"
    ))

    console.print("\nThis will create a new config.yaml file for your subject.\n")

    # Check if config.yaml already exists
    if os.path.exists('config.yaml'):
        overwrite = Confirm.ask(
            "[yellow]config.yaml already exists. Overwrite?[/yellow]",
            default=False
        )
        if not overwrite:
            console.print("[yellow]Initialization cancelled.[/yellow]")
            return False

    # Prompt for subject information
    console.print("[cyan]Subject Information:[/cyan]")

    subject_name = Prompt.ask(
        "  Subject name",
        default="Course Materials"
    )

    subject_short_name = Prompt.ask(
        "  Short name (3-5 letters for deck prefix)",
        default="".join([word[0].upper() for word in subject_name.split()[:3]])
    )

    subject_field = Prompt.ask(
        "  Field (e.g., Mathematics, Computer Science, Physics)",
        default="Education"
    )

    subject_description = Prompt.ask(
        "  Description",
        default=f"Educational materials for {subject_name}"
    )

    # Create config structure
    config = {
        'subject': {
            'name': subject_name,
            'short_name': subject_short_name,
            'field': subject_field,
            'description': subject_description
        },
        'prompts': {
            'system_context': f"You are generating flashcards for a {subject_field} course on {subject_name}.\nFocus on {subject_description}.\n",
            'card_quality_focus': [
                "Test understanding, not memorization",
                "Use concrete examples",
                "Keep calculations simple",
                "Focus on concepts and intuition"
            ],
            'example_cards': [
                {
                    'front': "Why does this concept work?",
                    'back': "It works because <strong>[add explanation here]</strong>",
                    'tags': "concept understanding"
                }
            ]
        },
        'processing': {
            'extract_images': True,
            'min_image_size': [100, 100],
            'image_format': 'png',
            'image_quality': 95
        },
        'output': {
            'markdown_dir': 'outputs/markdown',
            'images_dir': 'outputs/images',
            'anki_dir': 'outputs/anki',
            'apkg_dir': 'outputs/apkg'
        },
        'units': {},
        'card_distribution': {
            'conceptual': 0.40,
            'worked_examples': 0.20,
            'algorithm': 0.20,
            'pattern_recognition': 0.10,
            'visual': 0.10
        },
        'ollama': {
            'enabled': True,
            'base_url': 'http://localhost:11434',
            'model': 'ministral-3:8b',
            'timeout': 30,
            'batch_size': 5,
            'max_retries': 3,
            'description_length': 'concise'
        }
    }

    # Write config file
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[green]✓ Created config.yaml[/green]")

    # Create directory structure
    create_dirs = Confirm.ask(
        "\nCreate directory structure?",
        default=True
    )

    if create_dirs:
        dirs = [
            'pdfs',
            'outputs/markdown',
            'outputs/images',
            'outputs/anki',
            'outputs/apkg',
            'outputs/metadata'
        ]

        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✓ Created {dir_path}/[/green]")

    # Summary
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. Place your PDF files in the [cyan]pdfs/[/cyan] directory")
    console.print("2. Edit [cyan]config.yaml[/cyan] to add your units:")
    console.print("   [dim]units:")
    console.print("     \"lecture1.pdf\":")
    console.print("       unit_name: unit1_introduction")
    console.print("       target_cards: 50")
    console.print("       tags: [unit1, introduction][/dim]")
    console.print("3. Run [green]flashbang extract --all[/green] to extract PDFs")
    console.print("4. Run [green]flashbang generate --all[/green] to generate flashcards")
    console.print("5. Run [green]flashbang package --all[/green] to create .apkg files")

    console.print(f"\n[bold green]✓ Initialization complete for {subject_name}![/bold green]")

    return True
