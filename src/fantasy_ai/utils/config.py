"""
fantasy_ai/utils/config.py
--------------------------
Centralized environment/config loader for Fantasy AI.
Loads variables from the .env file into constants so they can
be imported anywhere in the project. Holds configuration constants and environment variable lookups
for league settings, API keys, and delivery parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parents[3] / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"✅ Loaded .env from {dotenv_path}")
else:
    # No .env file — rely on environment variables already set (e.g., in GitHub Actions)
    print(f"⚠️ .env file not found at {dotenv_path} — using existing environment variables")

# Load constants from environment
LEAGUE_ID = os.getenv("LEAGUE_ID")
SLEEPER_DISPLAY_NAME = os.getenv("SLEEPER_DISPLAY_NAME")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SEND_FROM = os.getenv("SEND_FROM")

# Debug to confirm (masking sensitive values)
def _mask(val, show=4):
    if not val:
        return None
    return val if len(val) <= show else val[:show] + "****"

print("DEBUG: LEAGUE_ID =", repr(LEAGUE_ID))
print("DEBUG: SLEEPER_DISPLAY_NAME =", repr(SLEEPER_DISPLAY_NAME))
print("DEBUG: SMTP_USER =", repr(_mask(SMTP_USER)))
print("DEBUG: EMAIL_TO =", repr(_mask(os.getenv("EMAIL_TO"))))
print("DEBUG: DISCORD_WEBHOOK =", repr(_mask(DISCORD_WEBHOOK)))
