"""
fantasy_ai/utils/config.py
--------------------------
Centralized environment/config loader for Fantasy AI.
Loads variables from the .env file into constants so they can
be imported anywhere in the project.
"""


import os
from dotenv import load_dotenv

# Load variables from .env in project root
load_dotenv()

LEAGUE_ID = os.getenv("LEAGUE_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")