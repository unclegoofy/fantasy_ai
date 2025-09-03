"""
fantasy_ai.reports.trade_radar

Identifies potential trade opportunities based on projected points,
positional depth, and ROS scores.
"""

from fantasy_ai.utils.helpers import normalize_name


def trade_radar(matchups, rosters, users, players, ros_scores, player_proj_map, week, my_display_name=None):
    """
    Return strategic trade targets based on scoring gaps, depth leverage, and matchup context.

    Only includes tips for the roster matching my_display_name.

    matchups: list from fetch_matchups()
    rosters: list from fetch_rosters()
    users: dict of user_id -> display_name
    players: dict of player_id -> player metadata
    ros_scores: dict of player_id -> ROS score
    player_proj_map: dict of player_id (str) -> projected points for this week
    week: int, current week number
    my_display_name: str, the display name of the roster owner to filter on
    """
    output = [f"\n📊 Trade Radar — Week {week}"]

    # 🔍 Map roster_id → projected points (team level)
    proj_map = {
        m["roster_id"]: float(m.get("display_points", m.get("projected_points", 0)) or 0.0)
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

    # Filter to lowest 3 projected teams
    low_proj = sorted(proj_map.items(), key=lambda x: x[1])[:3]

    for rid, proj in low_proj:
        owner = next((r for r in rosters if r["roster_id"] == rid), {})
        user_id = owner.get("owner_id")
        user_name = users.get(user_id, f"Roster {rid}")

        # Only show tips for my team
        if my_display_name and user_name != my_display_name:
            continue

        output.append(f"⚠️ {user_name} projected only {proj:.1f} pts")

        my_depth = depth_map.get(user_name, {})
        for other_name, other_depth in depth_map.items():
            if other_name == user_name:
                continue
            for pos in ["RB", "WR", "TE", "QB"]:
                if my_depth.get(pos, 0) < 2 and other_depth.get(pos, 0) > 3:
                    output.append(
                        f"  💡 Trade Tip: {user_name} should target a {pos} from {other_name} (depth: {other_depth[pos]})"
                    )

        # 🔍 Buy-low candidates (based on ROS score vs projection)
        bench = [pid for pid in owner.get("players", []) if pid not in owner.get("starters", [])]
        for pid in bench:
            p = players.get(pid, {})
            player_name = normalize_name(p)
            pos = p.get("position", "UNK")
            team = p.get("team", "FA")
            proj_pts = float(player_proj_map.get(str(pid), 0.0))
            ros_val = ros_scores.get(pid, 0)

            if ros_val > 140 and proj_pts < 9:
                output.append(
                    f"  🔍 Buy-low candidate: {player_name} ({pos}, {team}) — ROS: {ros_val:.1f}, projected {proj_pts:.1f} pts"
                )

        output.append("-" * 50)

    if len(output) == 1:
        output.append("  No trade insights for your team this week.")

    return "\n".join(output)