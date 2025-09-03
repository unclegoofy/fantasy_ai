"""
fantasy_ai.cli_helpers

Helper functions for CLI commands, including argument parsing,
output formatting, and integration with report/analysis modules.
"""

from fantasy_ai.utils.fetch import fetch_league_info
from fantasy_ai.utils.config import LEAGUE_ID

def fetch_current_week():
    """Fetch the current NFL week from Sleeper."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return 1
    league = fetch_league_info(LEAGUE_ID)
    return league.get("week") or 1