from fantasy_ai.api.sleeper_client import (
    get_league_info,
    get_matchups,
    get_users,
    get_rosters,
    get_players
)
from fantasy_ai.utils.config import LEAGUE_ID

def trade_radar(week_override=None):
    """Surface strategic trade targets based on scoring gaps, depth leverage, and matchup context."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return

    week = week_override or 1
    league = get_league_info(LEAGUE_ID)
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in get_users(LEAGUE_ID)}
    rosters = get_rosters(LEAGUE_ID)
    matchups = get_matchups(LEAGUE_ID, week)
    players = get_players()

    print(f"DEBUG: Trade Radar — Week {week}, {len(matchups)} matchups")

    proj_map = {m["roster_id"]: m.get("projected_points", 0) for m in matchups}

    # Build depth map by position
    depth_map = {}
    for r in rosters:
        rid = r["roster_id"]
        user = users.get(r.get("owner_id"), f"Roster {rid}")
        depth_map[user] = {}
        for pid in r.get("players", []):
            p = players.get(pid, {})
            pos = p.get("position", "UNK")
            depth_map[user][pos] = depth_map[user].get(pos, 0) + 1

    print(f"\n📊 Trade Radar — Week {week}")
    low_proj = sorted(proj_map.items(), key=lambda x: x[1])[:3]
    for rid, proj in low_proj:
        owner = next((r for r in rosters if r["roster_id"] == rid), {})
        user_id = owner.get("owner_id")
        name = users.get(user_id, f"Roster {rid}")
        print(f"⚠️ {name} projected only {proj:.1f} pts")

        my_depth = depth_map.get(name, {})
        for other_name, other_depth in depth_map.items():
            if other_name == name:
                continue
            for pos in ["RB", "WR", "TE", "QB"]:
                if my_depth.get(pos, 0) < 2 and other_depth.get(pos, 0) > 3:
                    print(f"  💡 Trade Tip: {name} should target a {pos} from {other_name} (depth: {other_depth[pos]})")

        # Mock buy-low candidates (replace with real scoring deltas later)
        bench = [p for p in owner.get("players", []) if p not in owner.get("starters", [])]
        for pid in bench:
            p = players.get(pid, {})
            name = p.get("full_name", "Unknown")
            pos = p.get("position", "UNK")
            team = p.get("team", "")
            proj = p.get("projected_points", 0)
            # Fake underperformance signal
            if proj > 8:
                print(f"  🔍 Buy-low candidate: {name} ({pos}, {team}) — projected {proj:.1f} pts, underperforming last 3 weeks")

        print("-" * 50)