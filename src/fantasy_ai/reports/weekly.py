from fantasy_ai.api.sleeper_client import get_league_info, get_matchups, get_users, get_rosters
from fantasy_ai.utils.config import LEAGUE_ID

def weekly_report(week_override=None):
    """Fetch and display matchups + projections for the given week."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return
    # ... rest of your old weekly_report logic ...