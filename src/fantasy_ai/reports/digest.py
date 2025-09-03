from fantasy_ai.scoring.ros_score import generate_ros_scores
from fantasy_ai.utils.fetch import fetch_players
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.reports.weekly import weekly_report
from fantasy_ai.reports.waivers import waivers
from fantasy_ai.reports.strategy import generate_weekly_strategy
from fantasy_ai.reports.trade_radar import trade_radar
from io import StringIO
import sys

def digest(week_override=None):
    """Generate full tactical digest for the given week."""
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    buffer = StringIO()
    sys.stdout = buffer

    print(f"\n📧 Weekly Digest — Week {week_override or 'Auto'}\n")

    # 🧠 Generate ROS scores once
    players = fetch_players()
    ros_scores = generate_ros_scores(players)

    # 🗓 Weekly Matchups + Projections
    print(weekly_report(week_override, include_ros=True))

    # 📥 Waiver Activity
    waivers(week_override, ros_scores=ros_scores)

    # 🧠 Strategy Digest
    print("\n🧠 Strategy Recommendations")
    print(generate_weekly_strategy(week_override, ros_scores=ros_scores))

    # 📊 Trade Radar
    print("\n📊 Trade Radar")
    trade_radar(week_override, ros_scores=ros_scores)

    sys.stdout = sys.__stdout__
    return buffer.getvalue()