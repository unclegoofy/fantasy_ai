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
    Raises for HTTP errors. Returns parsed JSON or empty dict on failure.
    """
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
        return {}

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

def fetch_matchups(league_id: str, week: int) -> List[Dict[str, Any]]:
    """
    Fetch all matchups for a specific week in the given league.
    Adds a 'display_points' key that falls back to projected_points if points == 0.
    """
    matchups = fetch(f"league/{league_id}/matchups/{week}")
    for m in matchups:
        actual = float(m.get("points", 0) or 0.0)
        proj = float(m.get("projected_points", 0) or 0.0)
        m["display_points"] = actual if actual > 0 else proj
    return matchups

def fetch_transactions(league_id: str, week: int) -> List[Dict[str, Any]]:
    """Fetch all transactions (waivers, trades, drops) for a given week."""
    return fetch(f"league/{league_id}/transactions/{week}")

def fetch_players() -> Dict[str, Dict[str, Any]]:
    """Fetch full player metadata for NFL (used for name/position lookups)."""
    return fetch("players/nfl")

def fetch_drafts(league_id: str) -> List[Dict[str, Any]]:
    """Fetch draft metadata for the given league (useful for dynasty/keeper)."""
    # TODO: Used by GitHub Actions workflow (strategy.yaml) for draft analysis.
    # Called indirectly via CLI / automation, so vulture will flag as unused.
    return fetch(f"league/{league_id}/drafts")

def fetch_state() -> Dict[str, Any]:
    """Fetch global Sleeper state (current NFL week, season, etc)."""
    # TODO: Used by GitHub Actions workflow (strategy.yaml) for league state checks.
    # Called indirectly via CLI / automation, so vulture will flag as unused.
    return fetch("state")