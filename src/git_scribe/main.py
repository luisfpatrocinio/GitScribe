import typer
from typing import Optional
from git_scribe import __version__, ui
from git_scribe.config import Config

# Create Typer application
app = typer.Typer(
    help="AI-powered Git commit message generator using Google Gemini.",
    add_completion=False,
    rich_markup_mode="rich"
)

def version_callback(value: bool):
    if value:
        ui.console.print(f"[bold cyan]{Config.APP_NAME}[/bold cyan] version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show the application version and exit.", callback=version_callback, is_eager=True
    )
):
    """
    GitScribe: Automate your git commits with AI.
    """
    pass

@app.command()
def commit(
    context: str = typer.Option("", "--context", "-c", help="Additional context for the AI (e.g. 'Fixing login bug')."),
    push: bool = typer.Option(False, "--push", "-p", help="Push changes to remote after commit."),
):
    """
    Analyze staged changes and generate a commit message.
    """
    ui.print_banner()
    ui.console.print(f"[info]Starting commit process...[/info]")
    
    if context:
        ui.console.print(f"[dim]Context provided: {context}[/dim]")
    
    if push:
        ui.console.print("[warning]Auto-push enabled.[/warning]")

    # TODO: Connect logic here later