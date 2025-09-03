"""
fantasy_ai.reports.weekly

Generates weekly matchup reports with projections and optional
rest-of-season scoring averages.
"""

from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.fetch import (
    fetch_league_info,
    fetch_matchups,
    fetch_users,
    fetch_rosters,
    fetch_players
)
from fantasy_ai.scoring.ros_score import generate_ros_scores

def weekly_report(week_override=None, include_ros=False):
    """Generate weekly matchup report with projections and optional ROS scoring."""
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    league = fetch_league_info(LEAGUE_ID)
    season = league.get("season")
    reported_week = league.get("week")

    week = week_override or reported_week
    if not isinstance(week, int) or week < 1 or week > 18:
        week = 1
        off_season_note = f"ℹ️ Sleeper reports week {reported_week} — likely off-season. Defaulting to week 1."
    else:
        off_season_note = None

    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in fetch_users(LEAGUE_ID)}
    rosters = fetch_rosters(LEAGUE_ID)
    roster_owner_map = {
        r["roster_id"]: users.get(r.get("owner_id"), f"Roster {r['roster_id']}")
        for r in rosters
    }

    matchups = fetch_matchups(LEAGUE_ID, week)
    players = fetch_players()
    ros_scores = generate_ros_scores(players) if include_ros else {}

    def avg_ros(roster):
        scores = [ros_scores.get(pid, 0) for pid in roster.get("players", [])]
        return round(sum(scores) / len(scores), 1) if scores else 0

    output = []
    if off_season_note:
        output.append(off_season_note)

    output.append(f"\n🏈 Weekly Report — {league.get('name')} (Season {season}) — Week {week}\n")

    seen_matchups = set()
    for m in matchups:
        mid = m.get("matchup_id")
        if mid in seen_matchups:
            continue
        seen_matchups.add(mid)

        teams = [mm for mm in matchups if mm.get("matchup_id") == mid]
        if len(teams) != 2:
            continue

        t1, t2 = teams
        name1 = roster_owner_map.get(t1["roster_id"], f"Roster {t1['roster_id']}")
        name2 = roster_owner_map.get(t2["roster_id"], f"Roster {t2['roster_id']}")

        # Use display_points (actual or projection fallback)
        pts1 = float(t1.get("display_points", 0))
        proj1 = float(t1.get("projected_points", 0))
        pts2 = float(t2.get("display_points", 0))
        proj2 = float(t2.get("projected_points", 0))

        ros1 = avg_ros(next((r for r in rosters if r["roster_id"] == t1["roster_id"]), {})) if include_ros else None
        ros2 = avg_ros(next((r for r in rosters if r["roster_id"] == t2["roster_id"]), {})) if include_ros else None

        line1 = f"{name1:20}  {pts1:5.1f} pts  (proj {proj1:5.1f})"
        line2 = f"{name2:20}  {pts2:5.1f} pts  (proj {proj2:5.1f})"

        if include_ros:
            line1 += f" — ROS avg: {ros1:.1f}"
            line2 += f" — ROS avg: {ros2:.1f}"

        output.extend([line1, line2, "-" * 50])

    return "\n".join(output)