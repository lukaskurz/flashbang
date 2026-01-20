"""
Analyze command - Check context window usage for flashcard generation.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

from src.config import load_config

console = Console()


def analyze_command(unit_name: str = None, target_cards: int = 60):
    """
    Analyze context window usage for flashcard generation.

    Args:
        unit_name: Unit name to analyze (if None, analyzes all)
        target_cards: Target card count for estimation
    """
    from src.flashcards.factory import create_card_generator

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]✗ Error loading configuration: {e}[/red]")
        return False

    # Get provider (always use ollama for analysis since it has context limits)
    try:
        generator = create_card_generator(config, provider='ollama')
    except Exception as e:
        console.print(f"[red]✗ Could not create Ollama generator: {e}[/red]")
        console.print("[yellow]Note: This command analyzes Ollama context usage[/yellow]")
        return False

    # Check if Ollama is available
    if not generator.check_availability():
        console.print("[red]✗ Ollama is not available[/red]")
        console.print("[yellow]Make sure Ollama is running (ollama serve)[/yellow]")
        return False

    # Get model info
    info = generator.get_provider_info()
    context_length = generator.client.get_context_length()

    console.print(Panel(
        f"[bold cyan]CONTEXT WINDOW ANALYSIS[/bold cyan]\n"
        f"[dim]Model: {info['model']} | Context: {context_length:,} tokens[/dim]"
    ))

    # If specific unit, analyze just that
    if unit_name:
        units_to_analyze = [unit_name]
    else:
        all_units = config.get_all_units()
        units_to_analyze = [info['unit_name'] for info in all_units.values()]

    if not units_to_analyze:
        console.print("[red]✗ No units found[/red]")
        return False

    # Create results table
    table = Table(title="Context Usage Analysis", show_header=True, header_style="bold cyan")
    table.add_column("Unit", style="cyan")
    table.add_column("Content", justify="right")
    table.add_column("Output Reserve", justify="right")
    table.add_column("Total Est.", justify="right")
    table.add_column("Utilization", justify="right")
    table.add_column("Status", justify="center")

    issues = []

    for unit in units_to_analyze:
        try:
            # Get page count for dynamic target
            page_count = generator.get_pdf_page_count(unit)
            if page_count > 0:
                effective_target = int(page_count * 1.5)
            else:
                effective_target = target_cards

            report = generator.get_context_usage_report(unit, effective_target)

            tokens = report['estimated_tokens']
            util = report['utilization_percent']

            # Determine status
            if report['content_fits']:
                if util < 70:
                    status = "[green]✓ OK[/green]"
                elif util < 90:
                    status = "[yellow]⚠ Tight[/yellow]"
                else:
                    status = "[yellow]⚠ Very Tight[/yellow]"
            else:
                status = "[red]✗ OVERFLOW[/red]"
                issues.append((unit, report))

            table.add_row(
                unit,
                f"{tokens['markdown_content']:,}",
                f"{tokens['output_reserve']:,}",
                f"{tokens['total']:,}",
                f"{util:.0f}%",
                status
            )

        except FileNotFoundError:
            table.add_row(
                unit,
                "-", "-", "-", "-",
                "[dim]No markdown[/dim]"
            )
        except Exception as e:
            table.add_row(
                unit,
                "-", "-", "-", "-",
                f"[red]Error: {str(e)[:20]}[/red]"
            )

    console.print(table)

    # Show detailed issues
    if issues:
        console.print("\n[bold red]⚠ Units with context overflow:[/bold red]")
        for unit, report in issues:
            console.print(f"\n[red]{unit}:[/red]")
            console.print(f"  Content tokens: {report['estimated_tokens']['markdown_content']:,}")
            console.print(f"  Available: {report['available_for_content']:,}")
            console.print(f"  Overflow: {report['overflow_tokens']:,} tokens")
            console.print(f"  [yellow]Recommendation: {report['recommendation']}[/yellow]")

    # Summary
    console.print()
    if not issues:
        console.print("[green]✓ All units fit within context window[/green]")
    else:
        console.print(f"[red]✗ {len(issues)} unit(s) may have context issues[/red]")
        console.print("\n[cyan]Possible solutions:[/cyan]")
        console.print("  1. Use a model with larger context (e.g., mistral, llama3)")
        console.print("  2. Split large units into smaller PDFs")
        console.print("  3. The generator will auto-truncate content if needed")

    return len(issues) == 0
