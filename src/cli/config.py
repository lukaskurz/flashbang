"""
Config command - Manage configuration settings.
"""

import yaml
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from src.config import load_config

console = Console()


def config_command(show=False, validate=False):
    """
    Manage configuration settings.

    Args:
        show: Show current configuration
        validate: Validate configuration
    """
    console.print(Panel.fit(
        "[bold cyan]Configuration Management[/bold cyan]",
        subtitle="anki-gen config"
    ))

    config_path = Path("config.yaml")

    if not config_path.exists():
        console.print("[red]✗ config.yaml not found[/red]")
        return False

    if show:
        # Show configuration file
        with open(config_path, 'r') as f:
            config_content = f.read()

        syntax = Syntax(config_content, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)

    if validate:
        # Validate configuration
        console.print("\n[cyan]Validating configuration...[/cyan]\n")

        try:
            config = load_config()

            # Check required directories
            dirs_table = Table(title="Directories", show_header=True, header_style="bold cyan")
            dirs_table.add_column("Directory", style="cyan")
            dirs_table.add_column("Path", style="dim")
            dirs_table.add_column("Status", justify="center")

            dirs = {
                "Markdown": config.markdown_dir,
                "Images": config.images_dir,
                "Anki": config.anki_dir,
                "APKG": config.apkg_dir
            }

            for name, path in dirs.items():
                exists = Path(path).exists()
                status = "[green]✓[/green]" if exists else "[yellow]missing[/yellow]"
                dirs_table.add_row(name, path, status)

            console.print(dirs_table)

            # Check units
            console.print()
            units = config.get_all_units()

            units_table = Table(title="Units", show_header=True, header_style="bold cyan")
            units_table.add_column("Unit", style="cyan")
            units_table.add_column("PDF", style="dim")
            units_table.add_column("Status", justify="center")

            for pdf_filename, unit_info in units.items():
                pdf_path = Path(f"pdfs/{pdf_filename}")
                exists = pdf_path.exists()
                status = "[green]✓[/green]" if exists else "[red]missing[/red]"
                units_table.add_row(unit_info['unit_name'], pdf_filename, status)

            console.print(units_table)

            # Check Ollama configuration
            console.print()
            ollama_config = config.config.get('ollama', {})

            ollama_table = Table(title="Ollama Configuration", show_header=False, box=None)
            ollama_table.add_column("Setting", style="cyan")
            ollama_table.add_column("Value", style="green")

            if ollama_config:
                ollama_table.add_row("Enabled", str(ollama_config.get('enabled', True)))
                ollama_table.add_row("Base URL", ollama_config.get('base_url', 'http://localhost:11434'))
                ollama_table.add_row("Model", ollama_config.get('model', 'ministral-3:8b'))
                ollama_table.add_row("Timeout", f"{ollama_config.get('timeout', 30)}s")
            else:
                ollama_table.add_row("Status", "[yellow]Not configured (using defaults)[/yellow]")

            console.print(ollama_table)

            # Test Ollama connection
            console.print()
            console.print("[cyan]Testing Ollama connection...[/cyan]")

            from src.ollama.client import OllamaClient
            client = OllamaClient()
            if client.check_availability():
                console.print("[green]✓ Ollama is available[/green]")
            else:
                console.print("[yellow]⚠ Ollama not available[/yellow]")

            console.print("\n[green]✓ Configuration is valid[/green]")

        except Exception as e:
            console.print(f"\n[red]✗ Configuration validation failed: {e}[/red]")
            return False

    if not show and not validate:
        # Default: show basic info
        try:
            config = load_config()

            info_table = Table(show_header=False, box=None)
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="green")

            info_table.add_row("Config File", "config.yaml")
            info_table.add_row("Units", str(len(config.get_all_units())))
            info_table.add_row("Output Dir", config.markdown_dir)

            console.print(info_table)

            console.print("\n[bold cyan]Options:[/bold cyan]")
            console.print("  [green]anki-gen config --show[/green] - Show full configuration")
            console.print("  [green]anki-gen config --validate[/green] - Validate configuration")

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    return True
