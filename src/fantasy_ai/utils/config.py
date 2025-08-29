"""
fantasy_ai/utils/config.py
--------------------------
Centralized environment/config loader for Fantasy AI.
Loads variables from the .env file into constants so they can
be imported anywhere in the project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parents[3] / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise FileNotFoundError(f".env file not found at {dotenv_path}")



LEAGUE_ID = os.getenv("LEAGUE_ID")
SLEEPER_DISPLAY_NAME = os.getenv("SLEEPER_DISPLAY_NAME")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SEND_FROM = os.getenv("SEND_FROM")

# Debug to confirm
print("DEBUG: LEAGUE_ID =", repr(LEAGUE_ID))
print("DEBUG: SLEEPER_DISPLAY_NAME =", repr(SLEEPER_DISPLAY_NAME))
