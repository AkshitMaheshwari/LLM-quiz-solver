"""
Configuration settings for the quiz solver
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Student Information
STUDENT_EMAIL = os.getenv("STUDENT_EMAIL", "")
STUDENT_SECRET = os.getenv("STUDENT_SECRET", "")

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "mixtral-8x7b-32768"

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Quiz Processing
QUIZ_TIMEOUT_SECONDS = 180  # 3 minutes
MAX_QUIZ_ATTEMPTS = 10
BROWSER_HEADLESS = True
BROWSER_TIMEOUT = 30000  # 30 seconds in ms

# LLM Configuration
LLM_MAX_TOKENS = 2048
LLM_TEMPERATURE = 0.7

# Validation
REQUIRED_VARS = ["STUDENT_EMAIL", "STUDENT_SECRET", "GROQ_API_KEY"]

def validate_config():
    """Validate that all required configuration is present"""
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please set them in .env file or as environment variables."
        )
    
    print(f"✓ Configuration validated")
    print(f"  Email: {STUDENT_EMAIL}")
    print(f"  Model: {GROQ_MODEL}")
    print(f"  Timeout: {QUIZ_TIMEOUT_SECONDS}s")
