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

# App configuration with Markdown Rich support in Help
app = typer.Typer(
    help="[bold cyan]GitScribe[/bold cyan]: The AI-powered CLI to automate your git workflow. ✍️ 🤖",
    add_completion=False,
    rich_markup_mode="rich"
)

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
        None, "--version", "-v", 
        help="Show the application version and exit.", 
        callback=version_callback, 
        is_eager=True
    )
):
    pass

@app.command()
def commit(
    context: str = typer.Option(
        "", "--context", "-c", 
        help="Provide [bold]extra context[/bold] to the AI (e.g., 'Fixing login bug')."
    ),
    auto: bool = typer.Option(
        False, "--auto", "-a", 
        help="[bold red]Auto Mode[/bold red]: Automatically stage all files, generate message, commit, and push without confirmation."
    ),
    style: CommitStyle = typer.Option(
        CommitStyle.default, "--style", "-s", 
        help="Select output style: [cyan]concise[/cyan] (title only), [cyan]default[/cyan] (standard), or [cyan]detailed[/cyan] (bullet points)."
    ),
    filter_ext: str = typer.Option(
        ".gml", "--filter", "-f", 
        help="Specific file extension to [bold]prioritize[/bold] if the git diff exceeds the size limit."
    )
):
    """
    [bold]Analyze[/bold] staged changes, [bold]generate[/bold] a commit message using Gemini AI, and [bold]commit[/bold] to the repository.
    """
    ui.print_banner()

    # 1. Repo Validation
    if not GitOps.is_git_repo():
        ui.console.print("[error]✖ Not a git repository.[/error]")
        raise typer.Exit(1)

    # 2. Staging Logic
    diff = GitOps.get_staged_diff()
    if not diff:
        ui.step_status("No staged changes found.", "wait")
        
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

    # 3. Size Handling
    if len(diff) > Config.MAX_DIFF_SIZE:
        ui.console.print(f"\n[warning]⚠ Diff is large ({len(diff)/1024:.1f}KB). using filter...[/warning]")
        diff = GitOps.get_staged_diff(only_extensions=[filter_ext])
        if not diff or len(diff) > Config.MAX_DIFF_SIZE:
             diff = "" 
             context += "\n(Full diff ignored due to size)"

    # 4. AI Generation
    try:
        generator = AIGenerator()
        message = generator.generate_commit_message(diff, context, style=style.value)
    except Exception as e:
        ui.console.print(f"[error]API Error: {e}[/error]")
        raise typer.Exit(1)

    # Display Result
    ui.console.print(Panel(
        Markdown(message), 
        title=f"[#0ce6f2]Generated ({style.value})[/] ✍️ 🤖", 
        border_style="#0098db"
    ))

    # 5. Confirmation Workflow
    should_commit = False
    
    if auto:
        should_commit = True
        ui.console.print("[bold #0ce6f2]🚀 Auto Mode enabled: Committing...[/bold #0ce6f2]")
    else:
        action = Prompt.ask(
            "[#0ce6f2]Action[/#0ce6f2]", 
            choices=["commit", "edit", "abort"], 
            default="commit"
        )
        if action == "abort":
            raise typer.Exit()
        elif action == "edit":
            GitOps.commit(message, edit=True)
            ui.console.print("[success]✔ Commit created![/success]")
            should_commit = False
        else:
            should_commit = True

    if should_commit:
        GitOps.commit(message)
        ui.console.print("[success]✔ Commit created![/success]")

    # 6. Push Logic
    should_push = auto

    if not auto and Confirm.ask("[secondary]Push changes?[/secondary]"):
        should_push = True

    if should_push:
        ui.step_status("Pushing to remote...", "wait")
        try:
            GitOps.push()
            ui.step_status("Push successful!", "done")
            
            # Show commit link if available
            commit_url = GitOps.get_commit_url()
            if commit_url:
                ui.print_commit_link(commit_url)

        except RuntimeError as e:
            if "no upstream branch" in str(e):
                current = GitOps.get_current_branch()
                if auto or Confirm.ask(f"Create upstream 'origin/{current}'?"):
                    GitOps.push(branch=current)
                    ui.step_status("Upstream set and pushed!", "done")
                    
                    # Also displays the link if you created upstream now
                    commit_url = GitOps.get_commit_url()
                    if commit_url:
                        ui.print_commit_link(commit_url)
            else:
                ui.console.print(f"[error]Push failed: {e}[/error]")

    # Footer comes last of all
    ui.print_footer()