from fantasy_ai.utils.helpers import normalize_name

def suggest_lineup_swaps(rosters, players, ros_scores, week):
    tips = []
    for r in rosters:
        starters = r.get("starters", [])
        bench = [p for p in r.get("players", []) if p not in starters]
        owner = r.get("owner_id", "Unknown")

        for s_pid in starters:
            s_player = players.get(s_pid, {})
            s_proj = float(s_player.get("projected_points") or ros_scores.get(s_pid, 0))
            if s_proj == 0 and s_player.get("position") in ["QB", "RB", "WR", "TE"]:
                continue
            for b_pid in bench:
                b_player = players.get(b_pid, {})
                b_proj = float(b_player.get("projected_points") or ros_scores.get(b_pid, 0))
                if b_proj > max(s_proj + 2, 10):
                    s_name = normalize_name(s_player)
                    b_name = normalize_name(b_player)
                    tips.append(f"  ✅ {owner}: Start {b_name} ({b_proj:.1f}) over {s_name} ({s_proj:.1f})")
    return tips