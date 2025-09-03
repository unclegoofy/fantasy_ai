"""
fantasy_ai.analysis.projected_outcome

Generates projected outcomes for matchups based on current rosters,
player projections, and scoring settings.
"""

def simulate_weekly_matchup(my_roster_ids, opp_roster_ids, matchups):
    """
    Returns projected points for both teams and win probability.

    Uses player-level projections from each matchup's 'player_points' dict
    (populated by fetch_matchups) if available. Falls back to 0.0 if no
    projection is found for a player.
    """
    # Build a single player_id -> projection map from all matchups
    player_proj_map = {}
    for m in matchups:
        player_points = m.get("player_points", {}) or {}
        for pid, pts in player_points.items():
            player_proj_map[str(pid)] = float(pts or 0.0)

    def total_proj(roster_ids):
        return sum(float(player_proj_map.get(str(pid), 0.0)) for pid in roster_ids)

    my_score = total_proj(my_roster_ids)
    opp_score = total_proj(opp_roster_ids)

    # Simple win probability model
    diff = my_score - opp_score
    if diff == 0:
        win_prob = 50
    elif diff > 0:
        win_prob = min(90, 50 + diff * 2)
    else:
        win_prob = max(10, 50 + diff * 2)

    return {
        "my_score": round(my_score, 1),
        "opp_score": round(opp_score, 1),
        "win_prob": round(win_prob, 1)
    }


def project_season_outcome(current_record, remaining_schedule, matchups):
    """
    Simulates remaining games and returns projected record and playoff odds.

    Uses player-level projections from matchups['player_points'] if available.
    """
    wins = current_record.get("wins", 0)
    losses = current_record.get("losses", 0)

    for matchup in remaining_schedule:
        my_roster = matchup.get("my_roster", [])
        opp_roster = matchup.get("opp_roster", [])
        result = simulate_weekly_matchup(my_roster, opp_roster, matchups)
        if result["win_prob"] >= 50:
            wins += 1
        else:
            losses += 1

    playoff_odds = (
        100 if wins >= 9 else
        70 if wins >= 7 else
        40 if wins >= 5 else
        10
    )

    return {
        "projected_record": f"{wins}-{losses}",
        "playoff_odds": f"{playoff_odds}%",
        "note": "Based on current roster and projected matchups"
    }