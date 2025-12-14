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

    def generate_commit_message(self, diff: str, context: str = "", style: str = "default") -> str:
        """
        Generates a commit message based on the diff and optional context.
        
        Args:
            diff: The git diff string.
            context: User provided context.
            style: 'default', 'concise', or 'detailed'.
        """
        
        base_instruction = (
            "You are an expert programmer writing a commit message following Conventional Commits specification.\n"
            "Format: <type>(<scope>): <subject>\n"
            "Use types: feat, fix, chore, docs, style, refactor, perf, test.\n"
        )

        # Dynamic instructions based on chosen style
        style_instruction = ""
        if style == "concise":
            style_instruction = (
                "STRICT CONSTRAINT: Output ONLY the subject line (first line). "
                "Do NOT write a body or description. Max 72 chars."
            )
        elif style == "detailed":
            style_instruction = (
                "INSTRUCTION: Provide a standard subject line, followed by a blank line, "
                "and then a detailed bulleted list (-) explaining the changes logic."
            )
        else:
            style_instruction = (
                "Keep the subject short. If necessary to explain 'why', add a brief body."
            )

        full_prompt = [
            base_instruction,
            style_instruction,
            f"User Context: {context}" if context else "",
            "\n--- BEGIN GIT DIFF ---\n",
            diff,
            "\n--- END GIT DIFF ---\n",
            "Generate the commit message:"
        ]

        # Spinner with the new palette color (#0ce6f2)
        with self.console.status("[#0ce6f2]Consulting Gemini AI...[/#0ce6f2]", spinner="dots"):
            try:
                response = self.model.generate_content(full_prompt)
                cleaned_message = response.text.strip().replace("`", "")
                return cleaned_message
            except Exception as e:
                raise RuntimeError(f"Gemini API Error: {str(e)}")