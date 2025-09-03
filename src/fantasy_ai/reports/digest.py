"""
fantasy_ai.reports.digest

Generates the full weekly digest by combining reports from
weekly matchups, waiver activity, strategy recommendations,
and trade radar.
"""

from fantasy_ai.scoring.ros_score import generate_ros_scores
from fantasy_ai.utils.fetch import fetch_players
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.reports.weekly import weekly_report
from fantasy_ai.reports.waivers import waivers
from fantasy_ai.analysis.strategist import generate_strategy_digest
from fantasy_ai.reports.trade_radar import trade_radar

def digest(week_override=None):
    """Generate full tactical digest for the given week."""
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    players = fetch_players()
    ros_scores = generate_ros_scores(players)

    sections = [
        f"\n📧 Weekly Digest — Week {week_override or 'Auto'}\n",
        weekly_report(week_override, include_ros=True),
        waivers(week_override, ros_scores=ros_scores),
        "\n🧠 Strategy Recommendations",
        generate_strategy_digest(week_override, ros_scores=ros_scores),
        "\n📊 Trade Radar",
        trade_radar(week_override, ros_scores=ros_scores)
    ]

    # Filter out any None values and join with newlines
    return "\n".join(s for s in sections if s)