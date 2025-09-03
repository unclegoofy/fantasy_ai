"""
fantasy_ai.analysis.recommendations

Provides tactical suggestions for adds, trades, and stashes based on
roster context, positional depth, and ROS upside.
"""

from fantasy_ai.utils.helpers import normalize_name


def recommend_adds(added_player_ids, players, my_display_name=None, users=None, rosters=None):
    """
    Recommend adds based on your own waiver activity.
    """
    if not added_player_ids or not players:
        return []

    lines = []
    for pid in added_player_ids:
        p = players.get(pid, {})
        name = normalize_name(p)
        pos = p.get("position", "UNK")
        team = p.get("team", "FA")
        lines.append(f"Added {name} ({pos}, {team}) — monitor usage this week")

    return lines


def recommend_trades(rosters, depth_map=None, my_display_name=None):
    """
    Recommend trade moves based on your positional depth.
    """
    if not rosters or not my_display_name:
        return []

    lines = []
    for r in rosters:
        owner_id = r.get("owner_id")
        owner_name = r.get("display_name", f"User {owner_id}")
        if owner_name != my_display_name:
            continue

        # Build depth map for this roster
        depth = {}
        for pid in r.get("players", []):
            p = r.get("player_metadata", {}).get(pid, {})
            pos = p.get("position", "UNK")
            depth[pos] = depth.get(pos, 0) + 1

        for pos in ["RB", "WR", "TE", "QB"]:
            if depth.get(pos, 0) < 2:
                lines.append(f"Consider trading for a {pos} — current depth: {depth.get(pos, 0)}")

    return lines


def recommend_stashes(players, roster=None, ros_scores=None, limit=5):
    """
    Suggest stash candidates based on positional need and ROS upside.
    Only considers players not already on the roster.
    """
    if not roster:
        return []

    rostered_ids = set(roster.get("players", []))
    depth_map = {}
    for pid in rostered_ids:
        p = players.get(pid, {})
        pos = p.get("position", "UNK")
        depth_map[pos] = depth_map.get(pos, 0) + 1

    # Filter unrostered players
    unrostered = [pid for pid in players if pid not in rostered_ids]

    stash_candidates = []
    for pid in unrostered:
        p = players.get(pid, {})
        pos = p.get("position", "UNK")
        team = p.get("team", "FA")
        ros_val = ros_scores.get(pid, 0.0) if ros_scores else 0.0
        if depth_map.get(pos, 0) < 2 and ros_val > 120:
            stash_candidates.append((ros_val, normalize_name(p), pos, team))

    stash_candidates.sort(reverse=True)
    return [f"Stash {name} ({pos}, {team}) — ROS: {ros:.1f}" for ros, name, pos, team in stash_candidates[:limit]]