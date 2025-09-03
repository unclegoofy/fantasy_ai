"""
fantasy_ai.cli

Command-line interface entry point for the Fantasy AI toolkit.
Parses CLI arguments, orchestrates report generation, and triggers
analysis modules. Intended for local execution or automation workflows.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# 🔧 Load environment variables from .env
load_dotenv()

# 🧠 Set PYTHONPATH for local imports (optional but helpful)
os.environ["PYTHONPATH"] = os.getenv("PYTHONPATH", "src")

# 📦 Core config and delivery
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.delivery import send_email, send_discord
from fantasy_ai.cli_helpers import fetch_current_week

# 📈 Reports Modules
from fantasy_ai.reports.weekly import weekly_report
from fantasy_ai.reports.waivers import waivers
from fantasy_ai.reports.trade_radar import trade_radar
from fantasy_ai.reports.digest import digest
from fantasy_ai.reports.strategy_engine import generate_weekly_strategy 

def run_digest(week: int):
    """Generate full digest and send via email/Discord."""
    output = digest(week_override=week)
    print(output)

    subject = f"Weekly Digest — Week {week}"
    send_email(subject, output)
    send_discord(output)

def run_strategy(week: int):
    """Generate strategy digest and send via email/Discord."""
    output = generate_weekly_strategy(week)
    print(output)

    subject = f"Strategy Digest — Week {week}"
    send_email(subject, output)
    send_discord(output)

def main():
    parser = argparse.ArgumentParser(description="Fantasy AI CLI")
    parser.add_argument(
        "command",
        choices=["weekly-report", "waivers", "trade-radar", "digest", "strategy"],
        help="Command to run"
    )
    parser.add_argument(
        "--week",
        type=int,
        help="NFL week number (optional, auto-detect if omitted)"
    )
    args = parser.parse_args()
    week = args.week or fetch_current_week()

    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        sys.exit(1)

    match args.command:
        case "weekly-report":
            weekly_report(week)
        case "waivers":
            waivers(week)
        case "trade-radar":
            trade_radar(week)
        case "digest":
            run_digest(week)
        case "strategy":
            run_strategy(week)

if __name__ == "__main__":
    main()