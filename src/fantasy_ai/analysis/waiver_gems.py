"""
fantasy_ai.analysis.waiver_gems

Identifies high-value waiver wire pickups based on projections,
ROS scores, and positional scarcity.
"""

def get_top_waiver_gems(players, ros_scores, rostered_ids, limit=5):
    unrostered = [pid for pid in ros_scores if pid not in rostered_ids]
    top = sorted(unrostered, key=lambda pid: ros_scores[pid], reverse=True)[:limit]
    return [players.get(pid, {}) for pid in top]