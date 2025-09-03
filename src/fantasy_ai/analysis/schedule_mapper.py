"""
fantasy_ai.analysis.schedule_mapper

Maps and analyzes team schedules for strength-of-schedule insights.
"""

TEAM_SCHEDULE = {
    "CAR": {15: "CIN"},
    "HOU": {15: "CIN"},
    "JAX": {15: "CIN"},
    "ARI": {15: "CIN"},
    "CIN": {15: "CAR"},
    # Add more teams as needed
}

def build_player_schedule(players, team_schedule=TEAM_SCHEDULE, target_week=15):
    """
    Returns a dict: player_id → opponent_team for target_week
    """
    player_schedule = {}
    for pid, p in players.items():
        team = p.get("team")
        if not team or team not in team_schedule:
            continue
        weekly_opponents = team_schedule.get(team, {})
        opponent = weekly_opponents.get(target_week)
        if opponent:
            player_schedule[pid] = {target_week: opponent}
    return player_schedule