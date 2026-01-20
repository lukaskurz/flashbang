#!/usr/bin/env python3
"""
Main entry point for the anki-gen CLI tool.

This unified CLI replaces the previous 4-script workflow:
- extract_pdfs.py → anki-gen extract
- generate_cards.py → anki-gen generate
- generate_apkg.py → anki-gen package
- (new) → anki-gen list
"""

import click
from rich.console import Console

from src.cli import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="anki-gen")
def cli():
    """
    Anki flashcard generation tool - Extract PDFs and generate decks automatically.

    Workflow:
    1. anki-gen init - Initialize configuration for a new subject
    2. anki-gen extract - Extract PDFs to markdown and images
    3. anki-gen generate - Generate flashcards from markdown
    4. anki-gen package - Package flashcards into .apkg files
    """
    pass


@cli.command()
def init():
    """Initialize configuration for a new subject."""
    from src.cli.init import init_command
    init_command()


@cli.command()
@click.option('--unit', '-u', help='Extract specific unit only')
@click.option('--no-images', is_flag=True, help='Skip image extraction')
@click.option('--no-describe', is_flag=True, help='Skip Ollama image descriptions')
def extract(unit, no_images, no_describe):
    """Extract PDFs to markdown with image descriptions."""
    from src.cli.extract import extract_command
    extract_command(unit, no_images, no_describe)


@cli.command()
@click.option('--unit', '-u', required=True, help='Unit to generate flashcards for')
@click.option('--show-images', is_flag=True, help='Display image descriptions in output')
def generate(unit, show_images):
    """Generate flashcards from markdown using Claude."""
    from src.cli.generate import generate_command
    generate_command(unit, show_images)


@cli.command()
@click.option('--unit', '-u', help='Package specific unit only')
@click.option('--all', 'package_all', is_flag=True, help='Package all units')
def package(unit, package_all):
    """Package flashcards into .apkg files."""
    from src.cli.package import package_command
    package_command(unit, package_all)


@cli.command()
@click.option('--detailed', is_flag=True, help='Show detailed unit information')
@click.option('--stats', is_flag=True, help='Show statistics')
def list(detailed, stats):
    """List available units and their status."""
    from src.cli.list import list_command
    list_command(detailed, stats)


@cli.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--validate', is_flag=True, help='Validate configuration')
def config(show, validate):
    """Manage configuration settings."""
    from src.cli.config import config_command
    config_command(show, validate)


if __name__ == '__main__':
    cli()
