import typer
from typing import Optional
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.markdown import Markdown

from git_scribe import __version__, ui
from git_scribe.config import Config
from git_scribe.git_ops import GitOps
from git_scribe.ai_ops import AIGenerator

app = typer.Typer(
    help="AI-powered Git commit message generator.",
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
        None, "--version", "-v", help="Show version.", callback=version_callback, is_eager=True
    )
):
    """GitScribe Entry Point"""
    pass

@app.command()
def commit(
    context: str = typer.Option("", "--context", "-c", help="Extra context for the AI."),
    auto_push: bool = typer.Option(False, "--push", "-p", help="Push after commit."),
    filter_ext: str = typer.Option(".gml", "--filter", "-f", help="Extension to prioritize if diff is huge.")
):
    """
    Generates a commit message from staged changes.
    """
    ui.print_banner()

    # Repo Validation
    if not GitOps.is_git_repo():
        ui.console.print("[bold red]✖ Error:[/bold red] Not a git repository.")
        raise typer.Exit(1)

    # Get Diff (with Auto-Stage logic)
    diff = GitOps.get_staged_diff()
    
    if not diff:
        ui.console.print("[yellow]No staged changes detected.[/yellow]")
        if Confirm.ask("Do you want to stage all files (git add .)?"):
            GitOps.stage_all()
            diff = GitOps.get_staged_diff()
            if not diff:
                ui.console.print("[red]Still no changes. Aborting.[/red]")
                raise typer.Exit()
        else:
            ui.console.print("[red]Aborted by user.[/red]")
            raise typer.Exit()

    # Large Diff Handling
    diff_len = len(diff)
    if diff_len > Config.MAX_DIFF_SIZE:
        ui.console.print(f"\n[bold yellow]⚠ Warning:[/bold yellow] Diff size ({diff_len/1024:.1f}KB) exceeds limit.")
        ui.console.print(f"Trying to filter for only [cyan]'{filter_ext}'[/cyan] files...")
        
        filtered_diff = GitOps.get_staged_diff(only_extensions=[filter_ext])
        
        if len(filtered_diff) > 0 and len(filtered_diff) <= Config.MAX_DIFF_SIZE:
            diff = filtered_diff
            ui.console.print(f"[green]✔ Used filtered diff ({len(diff)/1024:.1f}KB).[/green]")
        else:
            # If still too large or no files of that extension, ask for manual summary
            ui.console.print(f"[bold red]✖ Diff still too large.[/bold red] Please help the AI.")
            manual_summary = Prompt.ask("Enter a brief summary of changes")
            context = f"{manual_summary}\n(Note: Full diff ignored due to size)"
            diff = "" # Do not send the huge diff to the API

    # AI Generation
    try:
        generator = AIGenerator()
        message = generator.generate_commit_message(diff, context)
    except Exception as e:
        ui.console.print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(1)

    # Display and Menu
    ui.console.print("\n")
    ui.console.print(Panel(Markdown(message), title="[bold green]Generated Message[/bold green]", border_style="green"))
    ui.console.print("\n")

    action = Prompt.ask(
        "[bold cyan]Action[/bold cyan]", 
        choices=["commit", "edit", "abort"], 
        default="commit"
    )

    if action == "abort":
        ui.console.print("[red]Commit aborted.[/red]")
        raise typer.Exit()

    # Perform Commit
    try:
        GitOps.commit(message, edit=(action == "edit"))
        ui.console.print("[bold green]✔ Commit created successfully![/bold green]")
    except RuntimeError as e:
        ui.console.print(f"[bold red]Commit failed:[/bold red] {e}")
        raise typer.Exit(1)

    # Push Logic
    if auto_push or Confirm.ask("Do you want to push changes?"):
        ui.console.print("[dim]Pushing to remote...[/dim]")
        try:
            GitOps.push()
            ui.console.print("[bold green]✔ Push successful![/bold green]")
        except RuntimeError as e:
            # Simplified upstream error handling
            err_msg = str(e)
            if "no upstream branch" in err_msg or "set-upstream" in err_msg:
                ui.console.print("[yellow]⚠ No upstream branch found.[/yellow]")
                current_branch = GitOps.get_current_branch()
                if Confirm.ask(f"Create upstream for '{current_branch}'?"):
                    try:
                        GitOps.push(branch=current_branch)
                        ui.console.print("[bold green]✔ Upstream set and pushed![/bold green]")
                    except RuntimeError as fatal_e:
                        ui.console.print(f"[bold red]Push failed:[/bold red] {fatal_e}")
            else:
                ui.console.print(f"[bold red]Push failed:[/bold red] {err_msg}")