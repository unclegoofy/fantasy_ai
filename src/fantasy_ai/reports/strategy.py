from fantasy_ai.api.sleeper_client import (
    get_league_info,
    get_matchups,
    get_users,
    get_rosters,
    get_transactions,
    get_players
)
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.analysis.impact_score import score_waiver_target
from fantasy_ai.analysis.projected_outcome import simulate_weekly_matchup, project_season_outcome
from fantasy_ai.analysis.recommendations import recommend_adds, recommend_trades, recommend_stashes
from fantasy_ai.analysis.matchup_context import get_matchup_difficulty
from fantasy_ai.analysis.schedule_mapper import build_player_schedule, TEAM_SCHEDULE
from fantasy_ai.analysis.record_tracker import calculate_team_record
from fantasy_ai.analysis.ros_loader import load_ros_projections


def generate_weekly_strategy(week=None):
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    if week is None:
        league = get_league_info(LEAGUE_ID)
        week = league.get("week") or 1
        print(f"DEBUG: Auto‑detected current NFL week = {week}")

    output_lines = []
    players = get_players()
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in get_users(LEAGUE_ID)}
    rosters = get_rosters(LEAGUE_ID)

    print(f"DEBUG: Loaded {len(players)} players, {len(users)} users, {len(rosters)} rosters")

    # 1️⃣ Waiver Wire Analysis
    txns = get_transactions(LEAGUE_ID, week)
    print(f"DEBUG: Found {len(txns)} transactions for week {week}")
    added_player_ids = []

    for txn in txns:
        if txn["type"] not in ["waiver", "free_agent"]:
            continue
        adds = txn.get("adds") or {}
        for pid in adds:
            added_player_ids.append(pid)

    ros_data = load_ros_projections()
    ros_projection = {pid: ros_data.get(pid, 8.5) for pid in added_player_ids}
    position_pool = {
        "RB": added_player_ids,
        "WR": added_player_ids,
        "TE": added_player_ids,
        "QB": added_player_ids
    }

    player_schedule = build_player_schedule(players, TEAM_SCHEDULE, target_week=15)
    playoff_matchups = {
        pid: get_matchup_difficulty(players.get(pid, {}), week=15, player_schedule=player_schedule)
        for pid in added_player_ids
    }

    output_lines.append(f"📥 Waiver Targets — Week {week}")
    if added_player_ids:
        for pid in sorted(set(added_player_ids)):
            p = players.get(pid, {})
            if not p.get("full_name") and p.get("position") == "DEF":
                team = p.get("team", "Unknown")
                p["full_name"] = f"{team} DEF"
            summary = score_waiver_target(p, ros_projection, position_pool, playoff_matchups)
            output_lines.append(f"  - {summary}")
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

        for s_pid in starters:
            s_player = players.get(s_pid, {})
            s_proj = s_player.get("projected_points") or ros_projection.get(s_pid, 0)
            s_name = s_player.get("full_name", "Unknown")
            s_matchup = get_matchup_difficulty(s_player, week)

            for b_pid in bench:
                b_player = players.get(b_pid, {})
                b_proj = b_player.get("projected_points") or ros_projection.get(b_pid, 0)
                b_name = b_player.get("full_name", "Unknown")
                b_matchup = get_matchup_difficulty(b_player, week)

                if s_proj == 0 and s_player.get("position") in ["QB", "RB", "WR", "TE"]:
                    continue
                if b_proj > max(s_proj + 2, 10):
                    output_lines.append(
                        f"  ✅ {owner}: Start {b_name} ({b_proj:.1f} pts, {b_matchup}) over {s_name} ({s_proj:.1f} pts, {s_matchup})"
                    )

    # 4️⃣ Projected Outcome
    output_lines.append(f"\n🔮 Projected Outcome — Week {week}")
    my_roster = next((r for r in rosters if users.get(r.get("owner_id")) == "Kwilliams424"), None)
    matchup = next((m for m in matchups if m.get("roster_id") == my_roster.get("roster_id")), None) if my_roster else None

    my_matchup_id = matchup.get("matchup_id") if matchup else None
    opp_matchup = next(
        (m for m in matchups if m.get("matchup_id") == my_matchup_id and m.get("roster_id") != my_roster.get("roster_id")),
        None
    )
    opp_roster_id = opp_matchup.get("roster_id") if opp_matchup else None
    opp_roster = next((r for r in rosters if r.get("roster_id") == opp_roster_id), None)

    if not opp_roster and my_roster:
        fallback = next((r for r in rosters if r["roster_id"] != my_roster["roster_id"]), None)
        opp_roster = fallback

    print(f"DEBUG: My roster ID = {my_roster.get('roster_id') if my_roster else 'None'}")
    print(f"DEBUG: Opponent roster ID = {opp_roster_id}")
    print(f"DEBUG: Opponent roster found = {bool(opp_roster)}")

    if my_roster and opp_roster:
        my_starters = my_roster.get("starters", [])
        opp_starters = opp_roster.get("starters", [])
        result = simulate_weekly_matchup(my_starters, opp_starters, players)
        output_lines.append(
            f"  - Matchup vs {users.get(opp_roster.get('owner_id'), 'Unknown')}: "
            f"{result['my_score']} pts vs {result['opp_score']} pts → {result['win_prob']}% win probability"
        )

        current_record = calculate_team_record(my_roster["roster_id"], matchups)
        remaining_schedule = [{"my_roster": my_starters, "opp_roster": opp_starters} for _ in range(11)]
        season = project_season_outcome(current_record, remaining_schedule, players, my_roster["roster_id"])
        output_lines.append(
            f"  - Season projection: {season['projected_record']}, {season['playoff_odds']} playoff odds"
        )
    else:
        output_lines.append("  - Matchup or season projection unavailable")

    # 5️⃣ Recommendations
        output_lines.append(f"\n🧠 Recommendations")
    for line in recommend_adds(added_player_ids, players):
        output_lines.append(f"  {line}")
    for line in recommend_trades(rosters, depth_map):
        output_lines.append(f"  {line}")
    for line in recommend_stashes(players):
        output_lines.append(f"  {line}")

    return "\n".join(output_lines)
