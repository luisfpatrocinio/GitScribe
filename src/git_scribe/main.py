import typer
from typing import Optional
from enum import Enum
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.markdown import Markdown

from git_scribe import __version__, ui
from git_scribe.config import Config
from git_scribe.git_ops import GitOps
from git_scribe.ai_ops import AIGenerator

app = typer.Typer(
    help="AI-powered Git commit tool ✍🏼🤖",
    add_completion=False,
    rich_markup_mode="rich"
)

# Enum para facilitar a escolha do estilo
class CommitStyle(str, Enum):
    default = "default"
    concise = "concise"
    detailed = "detailed"

def version_callback(value: bool):
    if value:
        ui.console.print(f"[bold #0ce6f2]{Config.APP_NAME}[/bold #0ce6f2] v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    )
):
    pass

@app.command()
def commit(
    context: str = typer.Option("", "--context", "-c", help="Extra context for the AI."),
    auto: bool = typer.Option(False, "--auto", "-a", help="🚀 AUTO MODE: Stage all, Commit, and Push without confirmation."),
    style: CommitStyle = typer.Option(CommitStyle.default, "--style", "-s", help="Output style: concise, default, or detailed."),
    filter_ext: str = typer.Option(".gml", "--filter", "-f", help="Extension to filter if diff is huge.")
):
    """
    Generate, Commit, and (Optionally) Push.
    """
    ui.print_banner()

    # Repo Validation
    if not GitOps.is_git_repo():
        ui.console.print("[error]✖ Not a git repository.[/error]")
        raise typer.Exit(1)

    # 2. Staging Logic (Auto Mode skips prompts)
    diff = GitOps.get_staged_diff()
    if not diff:
        ui.step_status("No staged changes found.", "wait")
        
        # If in AUTO mode, do git add . directly
        if auto:
            ui.step_status("Auto-staging all files...", "wait")
            GitOps.stage_all()
            diff = GitOps.get_staged_diff()
        elif Confirm.ask("[secondary]Stage all files (git add .)?[/secondary]"):
            GitOps.stage_all()
            diff = GitOps.get_staged_diff()
        
        if not diff:
            ui.console.print("[error]Nothing to commit. Aborting.[/error]")
            raise typer.Exit()

    # Size Check and Filtering
    if len(diff) > Config.MAX_DIFF_SIZE:
        ui.console.print(f"\n[warning]⚠ Diff is large ({len(diff)/1024:.1f}KB). using filter...[/warning]")
        diff = GitOps.get_staged_diff(only_extensions=[filter_ext])
        if not diff or len(diff) > Config.MAX_DIFF_SIZE:
             diff = "" 
             context += "\n(Full diff ignored due to size)"

    # AI Commit Message Generation
    try:
        generator = AIGenerator()
        # Pass the chosen style (concise, detailed, default)
        message = generator.generate_commit_message(diff, context, style=style.value)
    except Exception as e:
        ui.console.print(f"[error]API Error: {e}[/error]")
        raise typer.Exit(1)

    # Display the generated message
    ui.console.print(Panel(
        Markdown(message), 
        title=f"[#0ce6f2]Generated ({style.value})[/] ✍🏼🤖", 
        border_style="#0098db"
    ))

    # Confirmation Flow
    should_commit = False
    
    if auto:
        should_commit = True
        ui.console.print("[bold #0ce6f2]🚀 Auto Mode enabled: Committing...[/bold #0ce6f2]")
    else:
        # Interactive menu
        action = Prompt.ask(
            "[#0ce6f2]Action[/#0ce6f2]", 
            choices=["commit", "edit", "abort"], 
            default="commit"
        )
        if action == "abort":
            raise typer.Exit()
        elif action == "edit":
            GitOps.commit(message, edit=True)
            # If edited, we assume it committed (git opens the editor)
            # But for the push flow below, we need to know if it worked
            # Simply put: we assume success if it didn't crashed
            ui.console.print("[success]✔ Commit created![/success]")
            should_commit = False # Already committed inside GitOps
        else:
            should_commit = True

    # Perform the commit if it was 'commit' or 'auto'
    if should_commit:
        GitOps.commit(message)
        ui.console.print("[success]✔ Commit created![/success]")

    # Push Logic
    should_push = auto # If auto, push is True by default

    if not auto and Confirm.ask("[secondary]Push changes?[/secondary]"):
        should_push = True

    if should_push:
        ui.step_status("Pushing to remote...", "wait")
        try:
            GitOps.push()
            ui.step_status("Push successful!", "done")
        except RuntimeError as e:
            # Lógica de Upstream (Simplificada para Auto)
            if "no upstream branch" in str(e):
                current = GitOps.get_current_branch()
                if auto or Confirm.ask(f"Create upstream 'origin/{current}'?"):
                    GitOps.push(branch=current)
                    ui.step_status("Upstream set and pushed!", "done")
            else:
                ui.console.print(f"[error]Push failed: {e}[/error]")