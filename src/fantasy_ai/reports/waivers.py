from fantasy_ai.api.sleeper_client import get_users, get_rosters, get_transactions, get_players
from fantasy_ai.utils.config import LEAGUE_ID

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