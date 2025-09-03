"""
fantasy_ai.reports.strategy_engine

Legacy or experimental strategy generation logic.
Consider merging into strategy.py if still in use.
"""

from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.fetch import (
    fetch_league_info,
    fetch_matchups,
    fetch_users,
    fetch_rosters,
    fetch_transactions,
    fetch_players
)
from fantasy_ai.analysis.impact_score import score_waiver_target
from fantasy_ai.analysis.projected_outcome import simulate_weekly_matchup, project_season_outcome
from fantasy_ai.analysis.recommendations import recommend_adds, recommend_trades, recommend_stashes
from fantasy_ai.analysis.matchup_context import get_matchup_difficulty
from fantasy_ai.analysis.schedule_mapper import build_player_schedule, TEAM_SCHEDULE
from fantasy_ai.analysis.record_tracker import calculate_team_record
from fantasy_ai.scoring.ros_score import generate_ros_scores
from fantasy_ai.utils.helpers import normalize_name

import os
SLEEPER_DISPLAY_NAME = os.getenv("SLEEPER_DISPLAY_NAME", "").strip()

def generate_weekly_strategy(week=None, ros_scores=None):
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    if week is None:
        league = fetch_league_info(LEAGUE_ID)
        week = league.get("week") or 1
        print(f"DEBUG: Auto‑detected current NFL week = {week}")

    output_lines = []
    players = fetch_players()
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in fetch_users(LEAGUE_ID)}
    rosters = fetch_rosters(LEAGUE_ID)
    ros_scores = ros_scores or generate_ros_scores(players)
    rostered_ids = {pid for r in rosters for pid in r.get("players", [])}

    # 🏆 Top 5 Waiver Gems
    unrostered = [pid for pid in ros_scores if pid not in rostered_ids]
    top_waivers = sorted(unrostered, key=lambda pid: ros_scores[pid], reverse=True)[:5]

    output_lines.append(f"\n🏆 Top Waiver Gems — Week {week}")
    for pid in top_waivers:
        p = players.get(pid, {})
        name = normalize_name(p)
        pos = p.get("position", "UNK")
        team = p.get("team", "FA")
        score = ros_scores[pid]
        output_lines.append(f"  ➕ {name:22} ({pos}, {team}) — ROS: {score:.1f}")

    print(f"DEBUG: Loaded {len(players)} players, {len(users)} users, {len(rosters)} rosters")

    # 1️⃣ Waiver Wire Analysis
    txns = fetch_transactions(LEAGUE_ID, week)
    print(f"DEBUG: Found {len(txns)} transactions for week {week}")
    added_player_ids = [
        pid for txn in txns if txn["type"] in ["waiver", "free_agent"]
        for pid in txn.get("adds", {})
    ]

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
            summary = score_waiver_target(p, ros_scores, position_pool, playoff_matchups)
            output_lines.append(f"  - {summary}")
    else:
        output_lines.append("  No notable waiver adds this week.")

    # 2️⃣ Trade Radar
    matchups = fetch_matchups(LEAGUE_ID, week)
    print(f"DEBUG: Found {len(matchups)} matchups for week {week}")

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

    output_lines.append(f"\n📊 Trade Radar — Week {week}")

    # ⚠️ Flag bottom 3 projected teams
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

    def normalize_name(p):
        if p.get("position") == "DEF" and not p.get("full_name"):
            return f"{p.get('team', 'Unknown')} DEF"
        return p.get("full_name") or p.get("last_name") or "Unknown"

    for r in rosters:
        owner = users.get(r.get("owner_id"), f"Roster {r['roster_id']}")
        starters = r.get("starters", [])
        bench = [p for p in r.get("players", []) if p not in starters]

        for s_pid in starters:
            s_player = players.get(s_pid, {})
            s_proj = float(s_player.get("projected_points") or ros_scores.get(s_pid, 0))
            s_name = normalize_name(s_player)
            s_matchup = get_matchup_difficulty(s_player, week)

            # Skip inactive or placeholder starters
            if s_proj == 0 and s_player.get("position") in ["QB", "RB", "WR", "TE"]:
                continue

            for b_pid in bench:
                b_player = players.get(b_pid, {})
                b_proj = float(b_player.get("projected_points") or ros_scores.get(b_pid, 0))
                b_name = normalize_name(b_player)
                b_matchup = get_matchup_difficulty(b_player, week)

                # Flag bench players with clear upside
                if b_proj > max(s_proj + 2, 10):
                    output_lines.append(
                        f"  ✅ {owner}: Start {b_name} ({b_proj:.1f} pts, {b_matchup}) over {s_name} ({s_proj:.1f} pts, {s_matchup})"
                    )
                    
    # 4️⃣ Projected Outcome
    output_lines.append(f"\n🔮 Projected Outcome — Week {week}")
    my_roster = next(
        (r for r in rosters if users.get(r.get("owner_id")) == SLEEPER_DISPLAY_NAME),
        None
    )
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