#!/usr/bin/env python3
"""
Main entry point for flashbang CLI.

This unified CLI replaces the previous 4-script workflow:
- extract_pdfs.py → flashbang extract
- generate_cards.py → flashbang generate
- generate_apkg.py → flashbang package
- (new) → flashbang list
"""

import click
from rich.console import Console

from src.cli import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="flashbang")
def cli():
    """
    flashbang - Bang out flashcards from PDFs instantly

    Workflow:
    1. flashbang init - Initialize configuration for a new subject
    2. flashbang extract - Extract PDFs to markdown and images
    3. flashbang generate - Generate flashcards from markdown
    4. flashbang package - Package flashcards into .apkg files
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
@click.option('--unit', '-u', help='Unit to generate flashcards for (if omitted, generates for all units)')
@click.option('--show-images', is_flag=True, help='Display image descriptions in output')
@click.option('--provider', '-p', type=click.Choice(['claude', 'ollama']),
              help='Override card generation provider (uses config default if not specified)')
def generate(unit, show_images, provider):
    """Generate flashcards from markdown using Claude or Ollama."""
    from src.cli.generate import generate_command
    generate_command(unit, show_images, provider)


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


@cli.command()
@click.option('--unit', '-u', help='Analyze specific unit (if omitted, analyzes all)')
@click.option('--target', '-t', type=int, default=60, help='Target card count for estimation')
def analyze(unit, target):
    """Analyze context window usage and content size for units.

    Helps diagnose why flashcard generation might fail or produce fewer cards
    than expected when using local Ollama models with limited context windows.
    """
    from src.cli.analyze import analyze_command
    analyze_command(unit, target)


if __name__ == '__main__':
    cli()
