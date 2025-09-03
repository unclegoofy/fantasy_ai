"""
fantasy_ai.analysis.impact_score

Calculates player impact scores based on performance metrics,
matchup difficulty, and positional value.
"""

def score_waiver_target(player, ros_projection, position_pool, playoff_matchups):
    """
    Returns a string with impact summary for a waiver add.
    """
    name = player.get("full_name", "Unknown")
    pos = player.get("position", "??")
    team = player.get("team", "")
    ros_pts = ros_projection.get(player.get("player_id"), 0)
    scarcity = len(position_pool.get(pos, []))
    playoff_note = playoff_matchups.get(player.get("player_id"), "")

    impact = "⭐ High Impact" if ros_pts > 8 and scarcity < 5 else "Moderate" if ros_pts > 5 else "Low"

    return f"{name} ({pos}, {team}) — {ros_pts:.1f} ROS pts, {playoff_note} {impact}"