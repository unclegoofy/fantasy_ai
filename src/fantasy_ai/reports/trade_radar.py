from fantasy_ai.api.sleeper_client import get_league_info, get_matchups, get_users, get_rosters, get_players
from fantasy_ai.utils.config import LEAGUE_ID

def trade_radar(week_override=None):
    """Surface strategic trade targets based on scoring gaps and roster depth."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return
    # ... rest of your old trade_radar logic ...