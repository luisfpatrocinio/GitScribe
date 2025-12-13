import subprocess
import shutil
from typing import List, Optional

class GitOps:
    """Handles all Git interactions via subprocess."""

    @staticmethod
    def _run(command: List[str], check: bool = True) -> str:
        """
        Executes a git command and returns the stdout.
        Raises subprocess.CalledProcessError if the command fails and check is True.
        """
        if not shutil.which("git"):
            raise RuntimeError("Git executable not found in PATH.")

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=check,
                encoding="utf-8",
                errors="replace"
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # Re-raise with the stderr for context
            raise RuntimeError(f"Git command failed: {e.stderr.strip()}") from e

    @staticmethod
    def is_git_repo() -> bool:
        """Checks if the current directory is inside a git work tree."""
        try:
            return GitOps._run(["git", "rev-parse", "--is-inside-work-tree"]) == "true"
        except (RuntimeError, subprocess.CalledProcessError):
            return False

    @staticmethod
    def stage_all() -> None:
        """Stages all changes (git add .)."""
        GitOps._run(["git", "add", "."])

    @staticmethod
    def get_staged_diff(exclude_extensions: Optional[List[str]] = None, 
                        only_extensions: Optional[List[str]] = None) -> str:
        """
        Gets the diff of staged files.
        
        Args:
            exclude_extensions: List of extensions to ignore (e.g. ['.lock']).
            only_extensions: List of extensions to include exclusive (e.g. ['.gml']).
        """
        cmd = ["git", "diff", "--cached"]
        
        if exclude_extensions:
            # Git syntax to exclude files: ':(exclude)*.ext'
            for ext in exclude_extensions:
                cmd.append(f":(exclude)*{ext}")
                
        if only_extensions:
            cmd.append("--")
            cmd.extend([f"*{ext}" for ext in only_extensions])

        return GitOps._run(cmd, check=False)

    @staticmethod
    def commit(message: str, edit: bool = False) -> None:
        """Creates a commit. Opens editor if edit=True."""
        cmd = ["git", "commit", "-m", message]
        if edit:
            cmd.append("--edit")
        GitOps._run(cmd)

    @staticmethod
    def push(remote: str = "origin", branch: Optional[str] = None) -> str:
        """
        Pushes changes. Handles the upstream setup logic internally would be too complex here,
        so we just try to push. The logic to set-upstream should be handled by the caller
        reacting to the error, or we can use the flag --set-upstream automatically if we want.
        """
        cmd = ["git", "push"]
        if branch:
            cmd.extend(["-u", remote, branch])
            
        return GitOps._run(cmd)

    @staticmethod
    def get_current_branch() -> str:
        return GitOps._run(["git", "rev-parse", "--abbrev-ref", "HEAD"])