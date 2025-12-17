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

# Configuração do App
app = typer.Typer(
    help="[bold cyan]GitScribe[/bold cyan]: AI-powered commit generator. ✍️ 🤖",
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

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    context: str = typer.Option(
        "", "--context", "-c", 
        help="Provide [bold]extra context[/bold] to the AI (e.g., 'Fixing login bug')."
    ),
    add_all: bool = typer.Option(
        False, "--add", "-A",
        help="[bold]Stage all files[/bold] (git add .) before generating the message."
    ),
    auto: bool = typer.Option(
        False, "--auto", "-a", 
        help="[bold red]Auto Mode[/bold red]: Automatically stage all files, generate message, commit, and push without confirmation."
    ),
    style: CommitStyle = typer.Option(
        CommitStyle.default, "--style", "-s", 
        help="Select output style: [cyan]concise[/cyan], [cyan]default[/cyan], or [cyan]detailed[/cyan]."
    ),
    filter_ext: str = typer.Option(
        ".gml", "--filter", "-f", 
        help="Specific file extension to [bold]prioritize[/bold] if the git diff exceeds the size limit."
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", 
        help="Show the application version and exit.", 
        callback=version_callback, 
        is_eager=True
    )
):
    """
    [bold]GitScribe[/bold] analyzes your staged changes and generates a semantic commit message using Gemini AI.
    """
    if ctx.invoked_subcommand is not None:
        return

    ui.print_banner()

    # 1. Repo Validation
    if not GitOps.is_git_repo():
        ui.console.print("[error]✖ Not a git repository.[/error]")
        raise typer.Exit(1)

    # 2. Staging Logic (Intelligent)
    
    # Se --auto ou --add foram passados, damos stage all imediatamente
    if auto or add_all:
        ui.step_status("Staging all files (forced)...", "wait")
        GitOps.stage_all()

    # Obtém o diff atual
    diff = GitOps.get_staged_diff()
    has_unstaged = GitOps.has_unstaged_changes()

    # Cenário: Usuário tem coisas staged, MAS esqueceu outras coisas unstaged
    if diff and has_unstaged and not auto:
        ui.console.print("\n[warning]⚠ You have staged changes, but there are also unstaged files.[/warning]")
        if Confirm.ask("[secondary]Do you want to include these unstaged files (git add .)? [/secondary]"):
            GitOps.stage_all()
            diff = GitOps.get_staged_diff() # Atualiza o diff
            ui.step_status("Updated staging area.", "done")
        else:
            ui.console.print("[dim]Ignoring unstaged files. Committing only staged changes.[/dim]\n")

    # Cenário: Nada staged 
    if not diff:
        ui.step_status("No staged changes found.", "wait")
        
        # Se auto estava ligado, já tentamos dar stage_all lá em cima. Se ainda tá vazio, é pq não tem nada mesmo.
        if auto: 
            ui.console.print("[error]Nothing to commit (directory clean).[/error]")
            raise typer.Exit()
            
        if has_unstaged:
            if Confirm.ask("[secondary]Stage all files (git add .)?[/secondary]"):
                GitOps.stage_all()
                diff = GitOps.get_staged_diff()
            else:
                ui.console.print("[error]Nothing to commit. Aborting.[/error]")
                raise typer.Exit()
        else:
            ui.console.print("[error]Nothing to commit (directory clean).[/error]")
            raise typer.Exit()

    # 3. Size Handling
    if len(diff) > Config.MAX_DIFF_SIZE:
        ui.console.print(f"\n[warning]⚠ Diff is large ({len(diff)/1024:.1f}KB). using filter...[/warning]")
        diff = GitOps.get_staged_diff(only_extensions=[filter_ext])
        if not diff or len(diff) > Config.MAX_DIFF_SIZE:
             diff = "" 
             safe_context = context if context else ""
             context = safe_context + "\n(Full diff ignored due to size)"

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
            
            commit_url = GitOps.get_commit_url()
            if commit_url:
                ui.print_commit_link(commit_url)

        except RuntimeError as e:
            if "no upstream branch" in str(e):
                current = GitOps.get_current_branch()
                if auto or Confirm.ask(f"Create upstream 'origin/{current}'?"):
                    GitOps.push(branch=current)
                    ui.step_status("Upstream set and pushed!", "done")
                    
                    commit_url = GitOps.get_commit_url()
                    if commit_url:
                        ui.print_commit_link(commit_url)
            else:
                ui.console.print(f"[error]Push failed: {e}[/error]")

    ui.print_footer()