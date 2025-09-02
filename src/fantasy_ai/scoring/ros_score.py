def generate_ros_scores(players: dict) -> dict:
    """
    Generate rest-of-season scores for Sleeper players using ADP and position weighting.
    Args:
        players (dict): Sleeper player metadata keyed by player_id.
    Returns:
        dict: {player_id: ros_score}
    """
    position_weights = {
        "QB": 1.0,
        "RB": 1.2,
        "WR": 1.1,
        "TE": 1.3,
        "K": 0.6,
        "DEF": 0.8,
    }

    ros_scores = {}
    for pid, data in players.items():
        adp = data.get("adp", None)
        pos = data.get("position", None)

        if adp is None or pos not in position_weights:
            continue

        base_score = round(200 - adp * 1.5, 1)  # Lower ADP = higher value
        weighted_score = round(base_score * position_weights[pos], 1)
        ros_scores[pid] = weighted_score

    return ros_scores