"""
fantasy_ai.analysis.waiver_gems

Identifies high-value waiver wire pickups based on projections,
ROS scores, and positional scarcity.
"""

def get_top_waiver_gems(players, ros_scores, rostered_ids, player_proj_map=None, my_roster=None, limit=5):
    """
    Returns top waiver gems for your team, filtered by positional need and ranked by ROS or W{week} projection.

    - Filters out players already on your roster.
    - Prioritizes positions where your depth < 2.
    - Ranks by ROS score if available, otherwise by current-week projection.
    """
    if not my_roster:
        return []

    # Build positional depth map for your roster
    my_depth_map = {}
    for pid in my_roster.get("players", []):
        p = players.get(pid, {})
        pos = p.get("position", "UNK")
        my_depth_map[pos] = my_depth_map.get(pos, 0) + 1

    # Filter unrostered players
    unrostered = [pid for pid in players if pid not in rostered_ids]

    # Prioritize positions where depth < 2
    def sort_key(pid):
        ros_val = ros_scores.get(pid, 0.0)
        proj_val = player_proj_map.get(str(pid), 0.0) if player_proj_map else 0.0
        return ros_val if ros_val > 0 else proj_val

    candidates = []
    for pid in unrostered:
        p = players.get(pid, {})
        pos = p.get("position", "UNK")
        if my_depth_map.get(pos, 0) >= 2:
            continue  # Skip positions where you're already covered

        ros_val = ros_scores.get(pid, 0.0)
        proj_val = player_proj_map.get(str(pid), 0.0) if player_proj_map else 0.0

        if ros_val > 0 or proj_val > 0:
            p_copy = p.copy()
            p_copy["ros_score"] = ros_val if ros_val > 0 else None
            p_copy["week_proj"] = proj_val if proj_val > 0 else None
            candidates.append(p_copy)

    # Sort and limit
    candidates.sort(key=lambda p: sort_key(p.get("player_id")), reverse=True)
    return candidates[:limit]

 