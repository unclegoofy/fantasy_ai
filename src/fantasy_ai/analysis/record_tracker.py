"""
fantasy_ai.analysis.record_tracker

Tracks team records, streaks, and playoff qualification scenarios.
"""

def calculate_team_record(roster_id, matchups):
    """
    Returns a dict: {"wins": X, "losses": Y}
    """
    wins = 0
    losses = 0

    for m in matchups:
        if m.get("roster_id") != roster_id:
            continue

        matchup_id = m.get("matchup_id")
        my_score = m.get("points", 0)

        # Find opponent in same matchup
        opp = next((x for x in matchups if x.get("matchup_id") == matchup_id and x.get("roster_id") != roster_id), None)
        opp_score = opp.get("points", 0) if opp else 0

        if my_score > opp_score:
            wins += 1
        elif my_score < opp_score:
            losses += 1

    return {"wins": wins, "losses": losses}