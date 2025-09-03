"""
fantasy_ai.analysis.lineup_optimizer

Suggests optimal starting lineups based on projections, ROS scores,
and positional depth.
"""

from fantasy_ai.utils.helpers import normalize_name


def suggest_lineup_swaps(rosters, players, ros_scores, week, player_proj_map=None, users=None, my_display_name=None):
    """
    Suggest bench-to-starter swaps for a specific roster (my_display_name) based on player-level projections and ROS scores.

    rosters: list of roster dicts from fetch_rosters()
    players: dict of player_id -> player metadata from fetch_players()
    ros_scores: dict of player_id -> ROS score
    week: int, current week number
    player_proj_map: optional dict of player_id (str) -> projected points for this week
    users: dict of user_id -> display_name
    my_display_name: str, the display name of the roster owner to filter on
    """
    tips = []
    for r in rosters:
        owner_id = r.get("owner_id", "Unknown")
        owner_name = users.get(owner_id, f"User {owner_id}") if users else owner_id

        # Only process my roster
        if my_display_name and owner_name != my_display_name:
            continue

        starters = r.get("starters", []) or []
        bench = [p for p in (r.get("players") or []) if p not in starters]

        for s_pid in starters:
            s_player = players.get(s_pid, {})
            # Prefer live projection from player_proj_map
            s_proj = None
            if player_proj_map is not None:
                s_proj = player_proj_map.get(str(s_pid))
            if s_proj is None:
                s_proj = s_player.get("projected_points") or ros_scores.get(s_pid, 0)
            s_proj = float(s_proj or 0.0)

            # Skip inactive/placeholder starters at core positions
            if s_proj == 0 and s_player.get("position") in ["QB", "RB", "WR", "TE"]:
                continue

            for b_pid in bench:
                b_player = players.get(b_pid, {})
                b_proj = None
                if player_proj_map is not None:
                    b_proj = player_proj_map.get(str(b_pid))
                if b_proj is None:
                    b_proj = b_player.get("projected_points") or ros_scores.get(b_pid, 0)
                b_proj = float(b_proj or 0.0)

                if b_proj > max(s_proj + 2, 10):
                    s_name = normalize_name(s_player)
                    b_name = normalize_name(b_player)
                    tips.append(
                        f"  ✅ {owner_name}: Start {b_name} ({b_proj:.1f}) over {s_name} ({s_proj:.1f})"
                    )

    if not tips:
        tips.append("  No lineup changes suggested this week.")

    return tips