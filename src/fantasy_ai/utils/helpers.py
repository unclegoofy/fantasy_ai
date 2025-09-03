"""
fantasy_ai.utils.helpers

Utility functions for name normalization, formatting, and other
common helper tasks used across modules.
"""

def normalize_name(p):
    """Return a clean display name for a player, handling DSTs and missing fields."""
    if not isinstance(p, dict):
        return "Unknown"
    if p.get("position") == "DEF" and not p.get("full_name"):
        return f"{p.get('team', 'Unknown')} DEF"
    return p.get("full_name") or p.get("last_name") or "Unknown"