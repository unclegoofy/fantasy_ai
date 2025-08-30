from fantasy_ai.api.sleeper_client import (
    get_league_info,
    get_matchups,
    get_users,
    get_rosters,
    get_transactions,
    get_players
)
from fantasy_ai.utils.config import LEAGUE_ID

def generate_weekly_strategy(week=None):
    """
    Build a real, data-driven weekly strategy digest.

    Sections:
    1. 📥 Waiver Wire Analysis — Lists actual waiver/free agent adds this week.
    2. 📊 Trade Radar — Flags lowest-projected teams and suggests positions to target.
    3. 📝 Lineup Optimization — Finds bench players projected to outscore starters.
    """
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    # Auto-detect week if not provided
    if week is None:
        league = get_league_info(LEAGUE_ID)
        week = league.get("week") or 1
        print(f"DEBUG: Auto‑detected current NFL week = {week}")

    output_lines = []
    players = get_players()
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in get_users(LEAGUE_ID)}
    rosters = get_rosters(LEAGUE_ID)

    # Debug counters
    print(f"DEBUG: Loaded {len(players)} players, {len(users)} users, {len(rosters)} rosters")

    # 1️⃣ Waiver Wire Analysis
    txns = get_transactions(LEAGUE_ID, week)
    print(f"DEBUG: Found {len(txns)} transactions for week {week}")
    waiver_targets = []
    for txn in txns:
        if txn["type"] not in ["waiver", "free_agent"]:
            continue
        adds = txn.get("adds") or {}
        for pid in adds:
            p = players.get(pid, {})
            name = p.get("full_name") or p.get("last_name") or "Unknown"
            pos = p.get("position", "??")
            team = p.get("team", "")
            waiver_targets.append(f"{name} ({pos}, {team})")

    output_lines.append(f"📥 Waiver Targets — Week {week}")
    if waiver_targets:
        for wt in sorted(set(waiver_targets)):
            output_lines.append(f"  - {wt}")
    else:
        output_lines.append("  No notable waiver adds this week.")

    # 2️⃣ Trade Radar
    matchups = get_matchups(LEAGUE_ID, week)
    print(f"DEBUG: Found {len(matchups)} matchups for week {week}")
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

    output_lines.append(f"\n📊 Trade Radar — Week {week}")
    low_proj = sorted(proj_map.items(), key=lambda x: x[1])[:3]
    for rid, proj in low_proj:
        owner = next((r for r in rosters if r["roster_id"] == rid), {})
        user_id = owner.get("owner_id")
        name = users.get(user_id, f"Roster {rid}")
        output_lines.append(f"⚠️ {name} projected only {proj:.1f} pts")
        my_depth = depth_map.get(name, {})
        for other_name, other_depth in depth_map.items():
            if other_name == name:
                continue
            for pos in ["RB", "WR", "TE", "QB"]:
                if my_depth.get(pos, 0) < 2 and other_depth.get(pos, 0) > 3:
                    output_lines.append(f"  💡 Consider trading for a {pos} from {other_name}")

    # 3️⃣ Lineup Optimization
    output_lines.append(f"\n📝 Lineup Tips — Week {week}")
    for r in rosters:
        owner = users.get(r.get("owner_id"), f"Roster {r['roster_id']}")
        starters = r.get("starters", [])
        bench = [p for p in r.get("players", []) if p not in starters]

        starter_proj = {pid: players.get(pid, {}).get("projected_points", 0) for pid in starters}
        bench_proj = {pid: players.get(pid, {}).get("projected_points", 0) for pid in bench}

        for s_pid, s_proj in starter_proj.items():
            for b_pid, b_proj in bench_proj.items():
                if b_proj > s_proj + 2:  # 2+ point difference
                    s_name = players.get(s_pid, {}).get("full_name", "Unknown")
                    b_name = players.get(b_pid, {}).get("full_name", "Unknown")
                    output_lines.append(
                        f"  ✅ {owner}: Start {b_name} ({b_proj:.1f} pts) over {s_name} ({s_proj:.1f} pts)"
                    )

    # Always return a string
    return "\n".join(output_lines)