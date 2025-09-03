"""
fantasy_ai.reports.waivers

Generates waiver wire activity reports for a given week,
annotated with optional ROS scores.
"""

from fantasy_ai.utils.fetch import fetch_users, fetch_rosters, fetch_transactions, fetch_players
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.helpers import normalize_name

def waivers(week=None, ros_scores=None):
    """Return waiver pickups and drops for a given week as a string."""
    if not LEAGUE_ID:
        return "❌ LEAGUE_ID not set in environment"

    week = week or 1
    players = fetch_players()
    users = {u["user_id"]: u.get("display_name", f"User {u['user_id']}") for u in fetch_users(LEAGUE_ID)}
    rosters = fetch_rosters(LEAGUE_ID)
    txns = fetch_transactions(LEAGUE_ID, week)

    output = [f"\n📥 Waiver Activity — Week {week}\n"]

    if not txns:
        output.append("No waiver transactions found.")
        return "\n".join(output)

    for txn in txns:
        if txn["type"] not in ["waiver", "free_agent", "trade"]:
            continue

        adds = txn.get("adds") or {}
        drops = txn.get("drops") or {}

        # Determine creator
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

        # Annotate adds with ROS score
        for pid in adds:
            p = players.get(pid, {})
            name = normalize_name(p)
            if p.get("position") == "DEF" and not p.get("full_name"):
                name = f"{p.get('team', 'Unknown')} DEF"
            pos = p.get("position", "??")
            score = ros_scores.get(pid, 0) if ros_scores else None
            annotation = f" — ROS: {score:.1f}" if score else ""
            output.append(f"➕ {name:25} ({pos}) added by {creator}{annotation}")

        for pid in drops:
            p = players.get(pid, {})
            name = normalize_name(p)
            if p.get("position") == "DEF" and not p.get("full_name"):
                name = f"{p.get('team', 'Unknown')} DEF"
            pos = p.get("position", "??")
            output.append(f"➖ {name:25} ({pos}) dropped by {creator}")

        if txn["type"] == "trade":
            output.append(f"🔄 Trade executed by {creator}")

        output.append("-" * 50)

    return "\n".join(output)