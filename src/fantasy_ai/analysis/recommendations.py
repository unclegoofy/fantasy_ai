"""
fantasy_ai.analysis.recommendations

Generates actionable recommendations for trades, waivers, and lineup changes.
"""

def recommend_adds(waiver_pool, players):
    """Suggest waiver adds based on projection and playoff matchup."""
    suggestions = []
    for pid in waiver_pool:
        p = players.get(pid, {})
        proj = p.get("projected_points", 0)
        pos = p.get("position", "UNK")
        team = p.get("team", "")
        if proj >= 8:
            suggestions.append(f"✅ Add {p.get('full_name', 'Unknown')} ({pos}, {team}) — projected {proj:.1f} pts")
    return suggestions

def recommend_trades(rosters, depth_map):
    """Suggest trade targets based on positional scarcity."""
    tips = []
    for name, depth in depth_map.items():
        for pos in ["RB", "WR", "TE", "QB"]:
            if depth.get(pos, 0) < 2:
                for other_name, other_depth in depth_map.items():
                    if other_name != name and other_depth.get(pos, 0) > 3:
                        tips.append(f"🔁 {name} should trade for a {pos} from {other_name} (depth: {other_depth[pos]})")
    return tips

def recommend_stashes(players, playoff_weeks=[15, 16, 17]):
    """Suggest stashes based on playoff matchups and upside."""
    stash_list = []
    for pid, p in players.items():
        if p.get("projected_points", 0) >= 7 and p.get("position") in ["RB", "WR", "TE"]:
            stash_list.append(f"📦 Stash {p.get('full_name', 'Unknown')} — upside for Weeks {playoff_weeks}")
    return stash_list[:5]  # Limit to top 5