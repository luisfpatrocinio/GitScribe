import google.generativeai as genai
from rich.console import Console
from git_scribe.config import Config

class AIGenerator:
    """Handles interactions with the Google Gemini API."""

    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=Config.GEMINI_MODEL,
            generation_config={"temperature": 0.7} # Balance between creativity and coherence
        )
        self.console = Console()

    def generate_commit_message(self, diff: str, context: str = "") -> str:
        """
        Generates a commit message based on the diff and optional context.
        """
        
        # The Master Prompt
        prompt = (
            "You are an expert programmer writing a commit message following Conventional Commits specification.\n"
            "Format: <type>(<scope>): <subject>\n\n"
            "Rules:\n"
            "1. Use types: feat, fix, chore, docs, style, refactor, perf, test.\n"
            "2. Keep the subject short (under 72 chars) and imperative (e.g., 'add' not 'added').\n"
            "3. If provided, use the context to understand the intent.\n"
            "4. Output ONLY the commit message. No markdown blocks, no 'Here is the commit'.\n"
        )

        full_prompt = [
            prompt,
            f"Context provided by user: {context}" if context else "",
            "\n--- BEGIN GIT DIFF ---\n",
            diff,
            "\n--- END GIT DIFF ---\n",
            "Generate the commit message:"
        ]

        # UI: Show Spinner while AI thinks
        with self.console.status("[bold cyan]Consulting Gemini AI...[/bold cyan]", spinner="dots"):
            try:
                response = self.model.generate_content(full_prompt)
                cleaned_message = response.text.strip().replace("`", "")
                return cleaned_message
            except Exception as e:
                raise RuntimeError(f"Failed to generate message: {str(e)}")