def get_current_week():
    """Fetch the current NFL week from Sleeper."""
    if not LEAGUE_ID:
        print("❌ LEAGUE_ID not set in environment")
        return 1
    league = get_league_info(LEAGUE_ID)
    return league.get("week") or 1