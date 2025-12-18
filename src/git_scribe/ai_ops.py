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
            generation_config={"temperature": 0.7}
        )
        self.console = Console()
        
        # Ensure data directory exists
        Config.ensure_data_dir()

    def _save_last_prompt(self, prompt_parts: list):
        """Saves the assembled prompt for debugging."""
        try:
            full_text = "\n".join([str(p) for p in prompt_parts])
            with open(Config.LAST_PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(full_text)
        except Exception:
            # Ignore log saving failures
            pass

    def generate_commit_message(self, diff: str, context: str = "", project_info: str = "", style: str = "default") -> str:
        base_instruction = (
            "You are an expert programmer writing a commit message following Conventional Commits specification.\n"
            "Format: <type>(<scope>): <subject>\n"
            "Use types: feat, fix, chore, docs, style, refactor, perf, test.\n"
        )

        style_instruction = ""
        if style == "concise":
            style_instruction = "STRICT: Output ONLY the subject line. Max 72 chars."
        elif style == "detailed":
            style_instruction = "INSTRUCTION: Provide a subject line, a blank line, and a detailed bulleted list."
        else:
            style_instruction = "Keep the subject short. If necessary, add a brief body."

        # Build prompt
        full_prompt = [
            base_instruction,
            style_instruction,
            f"Project Info: {project_info}" if project_info else "", 
            f"User Context: {context}" if context else "",
            "\n--- BEGIN GIT DIFF ---\n",
            diff,
            "\n--- END GIT DIFF ---\n",
            "Generate the commit message:"
        ]

        # Save log before sending
        self._save_last_prompt(full_prompt)

        with self.console.status("[#0ce6f2]Consulting Gemini AI...[/#0ce6f2]", spinner="dots"):
            try:
                response = self.model.generate_content(full_prompt)
                return response.text.strip().replace("`", "")
            except Exception as e:
                raise RuntimeError(f"Gemini API Error: {str(e)}")