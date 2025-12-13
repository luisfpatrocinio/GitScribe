import os
from pathlib import Path
from dotenv import load_dotenv

# Loads .env file variables
load_dotenv()

class Config:
    APP_NAME = "GitScribe"
    VERSION = "0.1.0"
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent
    
    # AI Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash-lite"
    
    # Git Settings
    MAX_DIFF_SIZE = 80000  # 80KB