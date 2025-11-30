import os
import sys

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Configuration ---
# Production: Use environment variables
# Development: Fallback to hardcoded values (migrated from ncc.py)

DISCORD_BOT_TOKEN = os.getenv(
    "DISCORD_BOT_TOKEN",
)

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
)

# Parse TARGET_CHANNEL_ID as integer
try:
    TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "1284807631772581999"))
except ValueError:
    print("Error: TARGET_CHANNEL_ID must be an integer.")
    sys.exit(1)

OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v3.2-exp")

