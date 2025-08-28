"""
fantasy_ai/api/sleeper_client.py
--------------------------------
Minimal client for Sleeper.com’s public API.
Provides typed wrapper functions for common league data needs.
"""

import os
import requests
from typing import Any, Dict, List, Optional

SLEEPER_API_BASE = "https://api.sleeper.app/v1"
VERBOSE = os.getenv("FANTASY_AI_VERBOSE", "false").lower() == "true"


def _get(endpoint: str) -> Any:
    """
    Internal helper for GET requests.
    Raises for HTTP errors. Returns parsed JSON or empty dict on failure.
    """
    url = f"{SLEEPER_API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    if VERBOSE:
        print(f"[GET] {url}")

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        if VERBOSE:
            print(f"❌ Failed to parse JSON from {url}")
        return {}


def get_league_info(league_id: str) -> Dict[str, Any]:
    """Fetch league metadata including scoring, roster positions, etc."""
    return _get(f"league/{league_id}")


def get_scoring_settings(league_id: str) -> Dict[str, Any]:
    """Convenience function: fetch scoring settings from league info."""
    league = get_league_info(league_id)
    return league.get("scoring_settings", {})


def get_users(league_id: str) -> List[Dict[str, Any]]:
    """Fetch all user profiles for the given league."""
    return _get(f"league/{league_id}/users")


def get_rosters(league_id: str) -> List[Dict[str, Any]]:
    """Fetch all roster objects for the given league."""
    return _get(f"league/{league_id}/rosters")


def get_matchups(league_id: str, week: int) -> List[Dict[str, Any]]:
    """Fetch all matchups for a specific week in the given league."""
    return _get(f"league/{league_id}/matchups/{week}")


def get_transactions(league_id: str, week: int) -> List[Dict[str, Any]]:
    """Fetch all transactions (waivers, trades, drops) for a given week."""
    return _get(f"league/{league_id}/transactions/{week}")


def get_players() -> Dict[str, Dict[str, Any]]:
    """Fetch full player metadata for NFL (used for name/position lookups)."""
    return _get("players/nfl")


def get_drafts(league_id: str) -> List[Dict[str, Any]]:
    """Fetch draft metadata for the given league (useful for dynasty/keeper)."""
    return _get(f"league/{league_id}/drafts")


def get_state() -> Dict[str, Any]:
    """Fetch global Sleeper state (current NFL week, season, etc)."""
    return _get("state")