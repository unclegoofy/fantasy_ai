# fantasy_ai/analysis/projected_outcome.py

def simulate_weekly_matchup(my_roster, opponent_roster, players):
    """
    Returns projected points for both teams and win probability.
    """
    def total_proj(roster):
        return sum(players.get(pid, {}).get("projected_points", 0) for pid in roster)

    my_score = total_proj(my_roster)
    opp_score = total_proj(opponent_roster)

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

def project_season_outcome(current_record, remaining_schedule, players, my_roster_id):
    """
    Simulates remaining games and returns projected record and playoff odds.
    """
    wins = current_record.get("wins", 0)
    losses = current_record.get("losses", 0)

    for matchup in remaining_schedule:
        my_roster = matchup.get("my_roster", [])
        opp_roster = matchup.get("opp_roster", [])
        result = simulate_weekly_matchup(my_roster, opp_roster, players)
        if result["win_prob"] >= 50:
            wins += 1
        else:
            losses += 1

    playoff_odds = 100 if wins >= 9 else 70 if wins >= 7 else 40 if wins >= 5 else 10

    return {
        "projected_record": f"{wins}-{losses}",
        "playoff_odds": f"{playoff_odds}%",
        "note": "Based on current roster and projected matchups"
    }