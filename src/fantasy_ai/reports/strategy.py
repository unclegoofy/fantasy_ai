from fantasy_ai.api.sleeper_client import get_league_info, get_matchups, get_users, get_rosters, get_transactions, get_players
from fantasy_ai.utils.config import LEAGUE_ID

def generate_weekly_strategy(week=None):
    """Build a real, data-driven weekly strategy digest."""
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"
    # ... rest of your old generate_weekly_strategy logic ...