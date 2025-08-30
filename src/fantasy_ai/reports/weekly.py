from fantasy_ai.api.sleeper_client import get_league_info, get_matchups, get_users, get_rosters
from fantasy_ai.utils.config import LEAGUE_ID

def weekly_report(week_override=None):
    """Fetch and display matchups + projections for the given week."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return

    league = get_league_info(LEAGUE_ID)
    season = league.get("season")
    reported_week = league.get("week")

    week = week_override or reported_week
    if not isinstance(week, int) or week < 1 or week > 18:
        print(f"ℹ️ Sleeper reports week {reported_week} — likely off-season. Defaulting to week 1.")
        week = 1

    print(f"\n🏈 Weekly Report — {league.get('name')} (Season {season}) — Week {week}\n")

    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in get_users(LEAGUE_ID)}
    rosters = get_rosters(LEAGUE_ID)
    roster_owner_map = {
        r["roster_id"]: users.get(r.get("owner_id"), f"Roster {r['roster_id']}")
        for r in rosters
    }

    matchups = get_matchups(LEAGUE_ID, week)
    seen_matchups = set()

    for m in matchups:
        mid = m["matchup_id"]
        if mid in seen_matchups:
            continue
        seen_matchups.add(mid)

        teams = [mm for mm in matchups if mm["matchup_id"] == mid]
        if len(teams) != 2:
            continue

        t1, t2 = teams
        name1 = roster_owner_map.get(t1["roster_id"], f"Roster {t1['roster_id']}")
        name2 = roster_owner_map.get(t2["roster_id"], f"Roster {t2['roster_id']}")

        pts1, proj1 = t1.get("points", 0), t1.get("projected_points", 0)
        pts2, proj2 = t2.get("points", 0), t2.get("projected_points", 0)

        print(f"{name1:20}  {pts1:5.1f} pts  (proj {proj1:5.1f})")
        print(f"{name2:20}  {pts2:5.1f} pts  (proj {proj2:5.1f})")
        print("-" * 50)