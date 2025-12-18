import os
from pathlib import Path
from dotenv import load_dotenv

# Load global API Key
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    APP_NAME = "GitScribe"
    
    # User data persistence
    USER_DATA_DIR = Path.home() / ".gitscribe"
    LAST_PROMPT_FILE = USER_DATA_DIR / "last_prompt.log"
    
    # AI Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash-lite"
    
    # Git Settings
    MAX_DIFF_SIZE = 80000
    
    # Project context configuration
    PROJECT_CONTEXT_FILE = ".gitscribe-context"

    @staticmethod
    def ensure_data_dir():
        """Ensure user data directory exists."""
        Config.USER_DATA_DIR.mkdir(parents=True, exist_ok=True)