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
        Styles: 
        - default: Standard conventional commit.
        - concise: Only the header (subject line).
        - detailed: Header + Bullet points body.
        """

        base_instruction = (
            "You are an expert programmer writing a commit message following Conventional Commits.\n"
            "Format: <type>(<scope>): <subject>\n"
        )

        style_instruction = ""
        if style == "concise":
            style_instruction = "IMPORTANT: Output ONLY the subject line. No body, no description. Max 72 chars."
        elif style == "detailed":
            style_instruction = "IMPORTANT: Provide a subject line, followed by a blank line, and then a bulleted list (-) explaining the changes in detail."
        else:
            style_instruction = "Keep the subject short. If necessary, add a brief body explaining 'why'."

        full_prompt = [
            base_instruction,
            style_instruction,
            f"Context: {context}" if context else "",
            "--- GIT DIFF ---",
            diff,
            "--- END DIFF ---",
            "Generate the commit message:"
        ]

        # UI: Show Spinner while AI thinks
        with self.console.status("[#0ce6f2]Consulting Gemini AI ✍🏼🤖...[/#0ce6f2]", spinner="dots"):
            try:
                response = self.model.generate_content(full_prompt)
                return response.text.strip().replace("`", "")
            except Exception as e:
                raise RuntimeError(f"Gemini Error: {str(e)}")