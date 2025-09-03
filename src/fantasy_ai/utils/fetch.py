"""
fantasy_ai.utils.fetch

Provides functions to fetch data from the Sleeper API, including
league info, rosters, matchups, transactions, and player data.
"""

import os
import requests
from typing import Any, Dict, List, Optional

SLEEPER_API_BASE = "https://api.sleeper.app/v1"
VERBOSE = os.getenv("FANTASY_AI_VERBOSE", "false").lower() == "true"


def fetch(endpoint: str) -> Any:
    """
    Internal helper for GET requests.
    Accepts either a relative API path (joined to SLEEPER_API_BASE)
    or a full URL (http/https). Raises for HTTP errors.
    Returns parsed JSON or empty dict/list on failure.
    """
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        url = endpoint
    else:
        url = f"{SLEEPER_API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"

    if VERBOSE:
        print(f"[FETCH] {url}")

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        if VERBOSE:
            print(f"❌ Failed to parse JSON from {url}")
        return {}  # or [] depending on expected type


def fetch_league_info(league_id: str) -> Dict[str, Any]:
    """Fetch league metadata including scoring, roster positions, etc."""
    return fetch(f"league/{league_id}")


def fetch_scoring_settings(league_id: str) -> Dict[str, Any]:
    """Convenience function: fetch scoring settings from league info."""
    league = fetch_league_info(league_id)
    return league.get("scoring_settings", {})


def fetch_users(league_id: str) -> List[Dict[str, Any]]:
    """Fetch all user profiles for the given league."""
    return fetch(f"league/{league_id}/users")


def fetch_rosters(league_id: str) -> List[Dict[str, Any]]:
    """Fetch all roster objects for the given league."""
    return fetch(f"league/{league_id}/rosters")


def fetch_rostered(league_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Return the roster object for the given user_id."""
    rosters = fetch_rosters(league_id)
    for r in rosters:
        if r.get("owner_id") == user_id:
            return r
    return None


def fetch_matchups(league_id: str, week: int):
    """
    Fetch matchups for a given week and merge in projections from Sleeper's
    public projections feed so pre-kickoff totals match the web UI.

    Adds to each matchup dict:
      - 'display_points': team-level projection or actual points
      - 'player_points': dict of player_id -> projected points for that week
                         (covers ALL players in the projections feed, not just starters)
    """
    # 1. Get the base matchups from Sleeper
    matchups = fetch(f"league/{league_id}/matchups/{week}")

    # 2. Fetch full player projections from Sleeper's .com feed
    projections_url = (
        f"https://api.sleeper.com/projections/nfl/2025/{week}"
        "?season_type=regular"
        "&position[]=DEF&position[]=FLEX&position[]=K"
        "&position[]=QB&position[]=RB&position[]=SUPER_FLEX"
        "&position[]=TE&position[]=WR"
        "&order_by=ppr"
    )
    projections = fetch(projections_url)

    # Normalize to dict keyed by player_id if API returned a list
    if isinstance(projections, list):
        projections = {str(p.get("player_id")): p for p in projections}

    # 3. Build a global player_id -> projected points map for ALL players in the feed
    global_player_points = {}
    for pid, proj_entry in projections.items():
        stats = proj_entry.get("stats", {})
        pts = stats.get("pts_ppr") or stats.get("pts") or 0.0
        global_player_points[str(pid)] = float(pts)

    # 4. Calculate team-level projected totals from starters
    calc_proj_totals = {}
    for m in matchups:
        starters = m.get("starters", []) or []
        total_proj = sum(global_player_points.get(str(pid), 0.0) for pid in starters)
        calc_proj_totals[m.get("roster_id")] = total_proj

    if VERBOSE:
        print("DEBUG: calc_proj_totals =", calc_proj_totals)

    # 5. Merge projections into each matchup
    for m in matchups:
        actual = float(m.get("points") or 0.0)
        proj = float(m.get("projected_points") or 0.0)

        # If Sleeper's team projection is missing/zero, use our calculated sum
        if proj == 0.0:
            proj = calc_proj_totals.get(m.get("roster_id"), 0.0)

        # display_points = actual if >0 else projection
        m["display_points"] = actual if actual > 0 else proj

        # Attach per-player projections for ALL players in the projections feed
        m["player_points"] = {
            str(pid): global_player_points.get(str(pid), 0.0)
            for pid in (m.get("players") or [])
        }

    return matchups

def fetch_transactions(league_id: str, week: int) -> List[Dict[str, Any]]:
    """Fetch all transactions (waivers, trades, drops) for a given week."""
    return fetch(f"league/{league_id}/transactions/{week}")


def fetch_players() -> Dict[str, Dict[str, Any]]:
    """Fetch full player metadata for NFL (used for name/position lookups)."""
    return fetch("players/nfl")


def fetch_drafts(league_id: str) -> List[Dict[str, Any]]:
    """Fetch draft metadata for the given league (useful for dynasty/keeper)."""
    return fetch(f"league/{league_id}/drafts")


def fetch_state() -> Dict[str, Any]:
    """Fetch global Sleeper state (current NFL week, season, etc)."""
    return fetch("state")