"""
fantasy_ai.reports.strategy_engine

Generates a weekly fantasy football strategy digest by orchestrating
waiver gems, trade radar, lineup optimization, and projected outcomes.
"""

import os
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.fetch import (
    fetch_league_info,
    fetch_matchups,
    fetch_users,
    fetch_rosters,
    fetch_transactions,
    fetch_players,
)
from fantasy_ai.scoring.ros_score import generate_ros_scores
from fantasy_ai.analysis.waiver_gems import get_top_waiver_gems
from fantasy_ai.reports.trade_radar import trade_radar
from fantasy_ai.analysis.lineup_optimizer import suggest_lineup_swaps
from fantasy_ai.analysis.projected_outcome import simulate_weekly_matchup, project_season_outcome
from fantasy_ai.analysis.record_tracker import calculate_team_record
from fantasy_ai.analysis.recommendations import recommend_adds, recommend_trades, recommend_stashes
from fantasy_ai.utils.helpers import normalize_name

SLEEPER_DISPLAY_NAME = os.getenv("SLEEPER_DISPLAY_NAME", "").strip()
VERBOSE = os.getenv("FANTASY_AI_VERBOSE", "false").lower() == "true"


def generate_weekly_strategy(week=None, ros_scores=None):
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    # Detect week if not provided
    if week is None:
        league = fetch_league_info(LEAGUE_ID)
        week = league.get("week") or 1
        if VERBOSE:
            print(f"DEBUG: Auto‑detected current NFL week = {week}")

    output_lines = [f"🧠 Strategy Digest — Week {week}"]

    # Core data
    players = fetch_players()
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in fetch_users(LEAGUE_ID)}
    rosters = fetch_rosters(LEAGUE_ID)
    my_roster = next((r for r in rosters if users.get(r.get("owner_id")) == SLEEPER_DISPLAY_NAME), None)
    matchups = fetch_matchups(LEAGUE_ID, week)

    # Build player-level projection map from matchups
    player_proj_map = {
        str(pid): pts
        for m in matchups
        for pid, pts in (m.get("player_points") or {}).items()
    }

    if ros_scores is None:
        ros_scores = generate_ros_scores(players)

    rostered_ids = {pid for r in rosters for pid in (r.get("players") or [])}

    # 🏆 Top Waiver Gems — personalized
    output_lines.append(f"\n🏆 Top Waiver Gems — Week {week}")
    top_waivers = get_top_waiver_gems(
        players,
        ros_scores,
        rostered_ids,
        player_proj_map=player_proj_map,
        my_roster=my_roster
    )
    for p in top_waivers:
        name = normalize_name(p)
        pos = p.get("position", "UNK")
        team = p.get("team", "FA")
        ros_val = p.get("ros_score")
        wk_proj = p.get("week_proj")
        ros_display = f"{ros_val:.1f}" if isinstance(ros_val, (int, float)) else "N/A"
        wk_display = f"{wk_proj:.1f}" if isinstance(wk_proj, (int, float)) else "N/A"
        output_lines.append(f"  ➕ {name:22} ({pos}, {team}) — ROS: {ros_display}, W{week} proj: {wk_display}")

    if not top_waivers:
        output_lines.append("  No waiver gems fit your roster needs this week.")

    # 📥 Waiver Targets
    txns = fetch_transactions(LEAGUE_ID, week)
    added_player_ids = []
    for txn in txns:
        if txn.get("type") in ("waiver", "free_agent"):
            adds = txn.get("adds") or {}
            if txn.get("creator") == SLEEPER_DISPLAY_NAME:
                added_player_ids.extend(adds.keys())
    added_player_ids = list(dict.fromkeys(added_player_ids))

    output_lines.append(f"\n📥 Waiver Targets — Week {week}")
    if added_player_ids:
        for pid in sorted(set(added_player_ids)):
            p = players.get(pid, {})
            if not p.get("full_name") and p.get("position") == "DEF":
                p["full_name"] = f"{p.get('team', 'Unknown')} DEF"
            ros_val = ros_scores.get(pid)
            wk_proj = player_proj_map.get(str(pid))
            ros_display = f"{ros_val:.1f}" if isinstance(ros_val, (int, float)) else "N/A"
            wk_display = f"{wk_proj:.1f}" if isinstance(wk_proj, (int, float)) else "N/A"
            output_lines.append(
                f"  - {normalize_name(p)} ({p.get('position')}, {p.get('team')}) — "
                f"ROS: {ros_display}, W{week} proj: {wk_display}"
            )
    else:
        output_lines.append("  No notable waiver adds this week.")

    # 📊 Trade Radar (new signature)
    output_lines.append(
        trade_radar(
            matchups,
            rosters,
            users,
            players,
            ros_scores,
            player_proj_map,
            week,
            my_display_name=SLEEPER_DISPLAY_NAME
        )
    )

    # 📝 Lineup Tips — position-aware
    output_lines.append(f"\n📝 Lineup Tips — Week {week}")

    FLEX_POSITIONS = {"WR", "RB", "TE"}

    def suggest_lineup_swaps(rosters, players, ros_scores, week, player_proj_map=None, users=None, my_display_name=None):
        tips = []
        my_roster = next((r for r in rosters if users.get(r.get("owner_id")) == my_display_name), None)
        if not my_roster:
            return tips

        starters = my_roster.get("starters", [])
        bench = [pid for pid in my_roster.get("players", []) if pid not in starters]

        for starter_id in starters:
            starter = players.get(starter_id, {})
            starter_proj = player_proj_map.get(str(starter_id), 0.0)
            starter_name = normalize_name(starter)
            starter_pos = starter.get("position", "UNK")

            for bench_id in bench:
                bench_player = players.get(bench_id, {})
                bench_proj = player_proj_map.get(str(bench_id), 0.0)
                bench_name = normalize_name(bench_player)
                bench_pos = bench_player.get("position", "UNK")

                # Only compare same-position or FLEX-compatible swaps
                same_pos = starter_pos == bench_pos
                flex_swap = starter_pos in FLEX_POSITIONS and bench_pos in FLEX_POSITIONS

                if (same_pos or flex_swap) and bench_proj > starter_proj + 1.0:
                    tips.append(
                        f"  ✅ {my_display_name}: Start {bench_name} ({bench_proj:.1f}) over {starter_name} ({starter_proj:.1f})"
                    )

    return tips

    # Extend with filtered tips
    output_lines.extend(
        suggest_lineup_swaps(
            rosters,
            players,
            ros_scores,
            week,
            player_proj_map=player_proj_map,
            users=users,
            my_display_name=SLEEPER_DISPLAY_NAME
        )
    )

    # 🔮 Projected Outcome
    output_lines.append(f"\n🔮 Projected Outcome — Week {week}")
    my_matchup_entry = next((m for m in matchups if m.get("roster_id") == my_roster.get("roster_id")), None) if my_roster else None
    my_matchup_id = my_matchup_entry.get("matchup_id") if my_matchup_entry else None
    opp_matchup = next(
        (m for m in matchups if m.get("matchup_id") == my_matchup_id and m.get("roster_id") != my_roster.get("roster_id")),
        None
    ) if my_matchup_id and my_roster else None
    opp_roster = next((r for r in rosters if r.get("roster_id") == opp_matchup.get("roster_id")), None) if opp_matchup else None

    if my_roster and opp_roster:
        my_starters = my_roster.get("starters", []) or []
        opp_starters = opp_roster.get("starters", []) or []
        result = simulate_weekly_matchup(my_starters, opp_starters, matchups)
        output_lines.append(
            f"  - Matchup vs {users.get(opp_roster.get('owner_id'), 'Unknown')}: "
            f"{result['my_score']} pts vs {result['opp_score']} pts → {result['win_prob']}% win probability"
        )
        current_record = calculate_team_record(my_roster["roster_id"], matchups)
        remaining_schedule = [{"my_roster": my_starters, "opp_roster": opp_starters} for _ in range(11)]
        season = project_season_outcome(current_record, remaining_schedule, matchups)
        output_lines.append(
            f"  - Season projection: {season['projected_record']}, {season['playoff_odds']} playoff odds"
        )
    else:
        output_lines.append("  - Matchup or season projection unavailable")

    # 🧠 Recommendations
    output_lines.append(f"\n🧠 Recommendations")
    adds = recommend_adds(added_player_ids, players, my_display_name=SLEEPER_DISPLAY_NAME)
    trades = recommend_trades(rosters, depth_map={}, my_display_name=SLEEPER_DISPLAY_NAME)
    stashes = recommend_stashes(players, roster=my_roster, ros_scores=ros_scores)

    if not any([adds, trades, stashes]):
        output_lines.append("  No specific recommendations this week.")
    else:
        for line in adds:
            output_lines.append(f"  {line}")
        for line in trades:
            output_lines.append(f"  {line}")
        for line in stashes:
            output_lines.append(f"  {line}")

    return "\n".join(output_lines)