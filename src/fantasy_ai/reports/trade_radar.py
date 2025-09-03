"""
fantasy_ai.reports.trade_radar

Identifies potential trade opportunities based on projected points,
positional depth, and ROS scores.
"""

from fantasy_ai.utils.fetch import (
    fetch_league_info,
    fetch_matchups,
    fetch_users,
    fetch_rosters,
    fetch_players
)
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.scoring.ros_score import generate_ros_scores
from fantasy_ai.utils.helpers import normalize_name

def trade_radar(week_override=None, ros_scores=None):
    """Return strategic trade targets based on scoring gaps, depth leverage, and matchup context."""
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    week = week_override or 1
    fetch_league_info(LEAGUE_ID)
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in fetch_users(LEAGUE_ID)}
    rosters = fetch_rosters(LEAGUE_ID)
    matchups = fetch_matchups(LEAGUE_ID, week)
    players = fetch_players()
    ros_scores = ros_scores or generate_ros_scores(players)

    output = []
    output.append(f"\n📊 Trade Radar — Week {week}")

    # 🔍 Map roster_id → projected points
    proj_map = {
        m["roster_id"]: float(m.get("projected_points", 0))
        for m in matchups if "roster_id" in m
    }

    # 🧠 Build positional depth map per user
    depth_map = {}
    for r in rosters:
        rid = r["roster_id"]
        user_name = users.get(r.get("owner_id"), f"Roster {rid}")
        depth_map[user_name] = {}
        for pid in r.get("players", []):
            p = players.get(pid, {})
            pos = p.get("position", "UNK")
            depth_map[user_name][pos] = depth_map[user_name].get(pos, 0) + 1

    low_proj = sorted(proj_map.items(), key=lambda x: x[1])[:3]

    for rid, proj in low_proj:
        owner = next((r for r in rosters if r["roster_id"] == rid), {})
        user_id = owner.get("owner_id")
        user_name = users.get(user_id, f"Roster {rid}")
        output.append(f"⚠️ {user_name} projected only {proj:.1f} pts")

        my_depth = depth_map.get(user_name, {})
        for other_name, other_depth in depth_map.items():
            if other_name == user_name:
                continue
            for pos in ["RB", "WR", "TE", "QB"]:
                if my_depth.get(pos, 0) < 2 and other_depth.get(pos, 0) > 3:
                    output.append(f"  💡 Trade Tip: {user_name} should target a {pos} from {other_name} (depth: {other_depth[pos]})")

        # 🔍 Buy-low candidates (based on ROS score vs projection)
        bench = [pid for pid in owner.get("players", []) if pid not in owner.get("starters", [])]
        for pid in bench:
            p = players.get(pid, {})
            player_name = normalize_name(p)
            pos = p.get("position", "UNK")
            team = p.get("team", "FA")
            proj_pts = float(p.get("projected_points", 0))
            ros_val = ros_scores.get(pid, 0)

            if ros_val > 140 and proj_pts < 9:
                output.append(f"  🔍 Buy-low candidate: {player_name} ({pos}, {team}) — ROS: {ros_val:.1f}, projected {proj_pts:.1f} pts")

        output.append("-" * 50)

    return "\n".join(output)