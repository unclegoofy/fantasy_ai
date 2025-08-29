from fantasy_ai.api.sleeper_client import get_users, get_rosters, get_transactions, get_players
from fantasy_ai.utils.config import LEAGUE_ID

def waivers(week_override=None):
    """Show waiver pickups and drops for a given week."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return
    # ... rest of your old waivers logic ...