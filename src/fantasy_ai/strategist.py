"""
fantasy_ai/strategist.py
------------------------
Generates a weekly strategy digest for your Sleeper fantasy league.
Pulls your roster, scoring settings, and matchups to produce
tactical recommendations for waivers, trades, and lineup optimization.
"""

from fantasy_ai.api.sleeper_client import (
    get_league_info,
    get_users,
    get_rostered,
    get_players,
    get_matchups,
    get_scoring_settings,
)
from fantasy_ai.utils.config import LEAGUE_ID, SLEEPER_DISPLAY_NAME


def generate_weekly_strategy(week: int) -> str:
    """Generate a tactical strategy digest for the given week."""
    print("DEBUG: strategist.py is running from:", __file__)
    print("DEBUG: SLEEPER_DISPLAY_NAME =", repr(SLEEPER_DISPLAY_NAME))

    league = get_league_info(LEAGUE_ID)
    users = get_users(LEAGUE_ID)

    # Debug: show all display names in the league
    print("DEBUG: Sleeper users:", [u["display_name"] for u in users])

    # Assign target_name before printing it
    target_name = SLEEPER_DISPLAY_NAME or "Kwilliams424"
    print("DEBUG: target_name =", target_name)

    # Case-insensitive partial match for robustness
    user_id = next(
        (
            u["user_id"]
            for u in users
            if target_name and target_name.lower() in u["display_name"].lower()
        ),
        None
    )

    if not user_id:
        return f"❌ Unable to resolve user_id for display name containing '{target_name}'"

    roster = get_rostered(LEAGUE_ID, user_id)
    if not roster:
        return f"❌ Unable to fetch roster for user_id {user_id}"

    players = get_players()
    scoring = get_scoring_settings(LEAGUE_ID)
    matchups = get_matchups(LEAGUE_ID, week)

    # Tactical analysis stubs — replace with real logic as needed
    analysis = analyze_roster(roster, players, scoring)
    waivers = suggest_waivers(roster, players, scoring)
    trades = suggest_trades(roster, players, scoring)
    lineup = optimize_lineup(roster, players, matchups, scoring)

    return format_strategy_digest(week, analysis, waivers, trades, lineup)


# --- Tactical modules (currently stubbed) ---

def analyze_roster(roster, players, scoring):
    return "📊 Roster Analysis:\n- WR depth strong\n- TE underperforming\n"


def suggest_waivers(roster, players, scoring):
    return "📥 Waiver Targets:\n- Add RB2 (proj 11.2 pts, +4.1 over current flex)\n"


def suggest_trades(roster, players, scoring):
    return "🔄 Trade Radar:\n- Offer WR3 + TE1 for RB1 upgrade\n"


def optimize_lineup(roster, players, matchups, scoring):
    return "🧠 Optimal Lineup:\n- Start QB2 vs weak defense (+3.8 pts)\n"


def format_strategy_digest(week, analysis, waivers, trades, lineup):
    return f"""📦 **Strategy Digest — Week {week}**

{analysis}
{waivers}
{trades}
{lineup}
"""
