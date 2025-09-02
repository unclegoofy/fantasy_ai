# fantasy_ai/analysis/matchup_context.py

# Mock defensive rankings by position (FantasyPros-style)

DEFENSE_RANKINGS = {
    "WR": {"CIN": 30, "CAR": 28, "ARI": 31},
    "RB": {"CIN": 29, "CAR": 30, "ARI": 32},
    "TE": {"CIN": 27, "CAR": 25, "ARI": 31},
    "QB": {"CIN": 26, "CAR": 24, "ARI": 30},
    "DEF": {"CIN": 31, "CAR": 29, "ARI": 32}
}

# Mock schedule: player_id → opponent team for given week
PLAYER_SCHEDULE = {
    "1234": {15: "CIN"},
    "5678": {15: "ARI"},
    "9101": {15: "NE"},
    # Add more as needed
}

def get_matchup_difficulty(player, week, player_schedule=None):
    """
    Returns matchup difficulty string for a player in a given week.
    Example: "W15 vs CIN (soft matchup)"
    """
    pid = player.get("player_id")
    pos = player.get("position", "UNK")
    opponent = player_schedule.get(pid, {}).get(week) if player_schedule else None
   
    if not opponent or pos not in DEFENSE_RANKINGS:
        return "Unknown matchup"

    rank = DEFENSE_RANKINGS[pos].get(opponent)
    if rank is None:
        return f"W{week} vs {opponent} (no data)"

    if rank <= 8:
        label = "tough matchup"
    elif rank <= 24:
        label = "neutral matchup"
    else:
        label = "soft matchup"

    return f"W{week} vs {opponent} ({label})"