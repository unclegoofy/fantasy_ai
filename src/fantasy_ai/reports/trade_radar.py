from fantasy_ai.api.sleeper_client import get_league_info, get_matchups, get_users, get_rosters, get_players
from fantasy_ai.utils.config import LEAGUE_ID

def trade_radar(week_override=None):
    """Surface strategic trade targets based on scoring gaps and roster depth."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return

    week = week_override or 1
    league = get_league_info(LEAGUE_ID)
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in get_users(LEAGUE_ID)}
    rosters = get_rosters(LEAGUE_ID)
    matchups = get_matchups(LEAGUE_ID, week)
    players = get_players()

    proj_map = {m["roster_id"]: m.get("projected_points", 0) for m in matchups}

    depth_map = {}
    for r in rosters:
        rid = r["roster_id"]
        user = users.get(r.get("owner_id"), f"Roster {rid}")
        depth_map[user] = {}
        for pid in r.get("players", []):
            p = players.get(pid, {})
            pos = p.get("position", "UNK")
            depth_map[user][pos] = depth_map[user].get(pos, 0) + 1

    print(f"\n📊 Trade Radar — Week {week}\n")

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
                    print(f"💡 Consider trading for a {pos} from {other_name}")
        print("-" * 50)