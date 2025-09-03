from fantasy_ai.utils.config import LEAGUE_ID, SLEEPER_DISPLAY_NAME
from fantasy_ai.utils.fetch import (
    fetch_league_info,
    fetch_users,
    fetch_rosters,
    fetch_players,
    fetch_matchups,
    fetch_transactions
)
from fantasy_ai.scoring.ros_score import generate_ros_scores
from fantasy_ai.analysis.waiver_gems import get_top_waiver_gems
from fantasy_ai.analysis.lineup_optimizer import suggest_lineup_swaps
from fantasy_ai.analysis.season_forecaster import forecast_season
from fantasy_ai.analysis.recommendations import (
    recommend_adds,
    recommend_trades,
    recommend_stashes
)
from fantasy_ai.analysis.projected_outcome import simulate_weekly_matchup
from fantasy_ai.utils.helpers import normalize_name

def generate_strategy_digest(week=None, ros_scores=None):
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    league = fetch_league_info(LEAGUE_ID)
    week = week or league.get("week") or 1
    players = fetch_players()
    users = {
        u["user_id"]: u.get("display_name", f"User {u['user_id']}")
        for u in fetch_users(LEAGUE_ID)
    }
    rosters = fetch_rosters(LEAGUE_ID)
    matchups = fetch_matchups(LEAGUE_ID, week)
    txns = fetch_transactions(LEAGUE_ID, week)
    ros_scores = ros_scores or generate_ros_scores(players)

    output_lines = [f"\n🧠 Strategy Digest — Week {week}"]

    # 🏆 Waiver Gems
    rostered_ids = {pid for r in rosters for pid in r.get("players", [])}
    top_waivers = get_top_waiver_gems(players, ros_scores, rostered_ids)
    output_lines.append("\n🏆 Top Waiver Gems")
    for p in top_waivers:
        name = normalize_name(p)
        pos = p.get("position", "UNK")
        team = p.get("team", "FA")
        score = ros_scores.get(p.get("player_id"), 0)
        output_lines.append(f"  ➕ {name:22} ({pos}, {team}) — ROS: {score:.1f}")

    # 📝 Lineup Optimization
    output_lines.append("\n📝 Lineup Optimization")
    lineup_tips = suggest_lineup_swaps(rosters, players, ros_scores, week)
    output_lines.extend(lineup_tips)

    # 🔮 Matchup Forecast
    output_lines.append("\n🔮 Matchup Forecast")
    my_roster = next(
        (r for r in rosters if users.get(r.get("owner_id")) == SLEEPER_DISPLAY_NAME),
        None
    )
    opp_roster = next(
        (r for r in rosters if r["roster_id"] != my_roster["roster_id"]),
        None
    ) if my_roster else None

    if my_roster and opp_roster:
        result = simulate_weekly_matchup(
            my_roster.get("starters", []),
            opp_roster.get("starters", []),
            players
        )
        season = forecast_season(my_roster, opp_roster, matchups, players)
        output_lines.append(f"  - Win Prob: {result['win_prob']}%")
        output_lines.append(f"  - Season Projection: {season['projected_record']}, {season['playoff_odds']} playoff odds")

    # 🧠 Recommendations
    output_lines.append("\n🧠 Recommendations")

    # Waiver adds
    waiver_pool = [
        pid for txn in txns
        if txn["type"] in ["waiver", "free_agent"]
        for pid in (txn.get("adds") or {})
    ]
    
    output_lines.extend(recommend_adds(waiver_pool, players))

    # Depth map for trade tips
    depth_map = {}
    for r in rosters:
        name = users.get(r.get("owner_id"), f"Roster {r['roster_id']}")
        depth_map[name] = {}
        for pid in r.get("players", []):
            pos = players.get(pid, {}).get("position", "UNK")
            depth_map[name][pos] = depth_map[name].get(pos, 0) + 1

    output_lines.extend(recommend_trades(rosters, depth_map))
    output_lines.extend(recommend_stashes(players))

    return "\n".join(output_lines)