"""
fantasy_ai/cli.py
-----------------
Command-line interface for Fantasy AI.
Usage examples:
    python -m fantasy_ai.cli weekly-report
    python -m fantasy_ai.cli waivers --week 3
    python -m fantasy_ai.cli trade-radar
    python -m fantasy_ai.cli digest
    python -m fantasy_ai.cli strategy --week 5
"""

import argparse
from fantasy_ai.api.sleeper_client import (
    get_league_info,
    get_matchups,
    get_users,
    get_rosters,
    get_transactions,
    get_players
)
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.delivery import send_email, send_discord


# ---------------------------
# Helper: Auto-detect NFL week
# ---------------------------
def get_current_week():
    """Fetch the current NFL week from Sleeper."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return 1
    league = get_league_info(LEAGUE_ID)
    return league.get("week") or 1


# ---------------------------
# Core report functions
# ---------------------------
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


def waivers(week_override=None):
    """Show waiver pickups and drops for a given week."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return

    week = week_override or 1
    players = get_players()
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in get_users(LEAGUE_ID)}
    rosters = get_rosters(LEAGUE_ID)
    txns = get_transactions(LEAGUE_ID, week)

    print(f"\n📥 Waiver Activity — Week {week}\n")

    if not txns:
        print("No waiver transactions found.")
        return

    for txn in txns:
        if txn["type"] not in ["waiver", "free_agent", "trade"]:
            continue

        creator_id = txn.get("creator_id")
        roster_id = txn.get("roster_ids", [None])[0]
        creator = "Unknown"

        if creator_id:
            creator = users.get(creator_id, f"User {creator_id}")
        elif roster_id is not None:
            roster_owner = next((r for r in rosters if r["roster_id"] == roster_id), None)
            if roster_owner:
                user_id = roster_owner.get("owner_id")
                creator = users.get(user_id, f"User {user_id}")

        adds = txn.get("adds") or {}
        drops = txn.get("drops") or {}

        for pid in adds:
            p = players.get(pid, {})
            name = p.get("full_name") or p.get("last_name") or "Unknown"
            if p.get("position") == "DEF" and not p.get("full_name"):
                name = f"{p.get('team', 'Unknown')} DEF"
            pos = p.get("position", "??")
            print(f"➕ {name:25} ({pos}) added by {creator}")

        for pid in drops:
            p = players.get(pid, {})
            name = p.get("full_name") or p.get("last_name") or "Unknown"
            if p.get("position") == "DEF" and not p.get("full_name"):
                name = f"{p.get('team', 'Unknown')} DEF"
            pos = p.get("position", "??")
            print(f"➖ {name:25} ({pos}) dropped by {creator}")

        if txn["type"] == "trade":
            print(f"🔄 Trade executed by {creator}")
        print("-" * 50)


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


# ---------------------------
# Digest wrapper
# ---------------------------
def digest(week_override=None):
    """Run weekly-report, waivers, and trade-radar in sequence and deliver output."""
    from io import StringIO
    import sys

    if week_override is None:
        week_override = get_current_week()
        print(f"DEBUG: Auto‑detected current NFL week = {week_override}")

    buffer = StringIO()
    sys.stdout = buffer
()