from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "command": "bold magenta",
})

console = Console(theme=custom_theme)

def print_banner():
    """Exibe o banner inicial."""
    console.print(
        "[bold cyan]GitScribe[/bold cyan] [dim]v0.1.0[/dim] | [italic]AI-Powered Commit Tool[/italic]",
        style="blue"
    )
    console.print("-" * 50, style="dim")