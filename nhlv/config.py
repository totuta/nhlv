"""Local nhlv preferences, including favourite teams."""

from __future__ import annotations

import os
from pathlib import Path


def _read_values(path: Path, key: str) -> list[str]:
    if not path.is_file():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(f"{key}="):
            return [item.strip() for item in line[len(key) + 1 :].split(",") if item.strip()]
    return []


def favorite_teams() -> list[str]:
    """Read NHLV_FAVORITES, nhlv config, then the existing mlbv config."""
    env_value = os.environ.get("NHLV_FAVORITES", "")
    if env_value:
        return [item.strip().upper() for item in env_value.split(",") if item.strip()]
    home = Path.home()
    nhlv_favs = [item.upper() for item in _read_values(home / ".config" / "nhlv" / "config", "favs")]
    if nhlv_favs:
        return nhlv_favs
    return [item.upper() for item in _read_values(home / ".config" / "mlbv" / "config", "favs")]


def favorite_players() -> list[str]:
    """Read favourite player last names from the NHL-specific config."""
    env_value = os.environ.get("NHLV_FAVORITE_PLAYERS", "")
    if env_value:
        return [item.strip().lower() for item in env_value.split(",") if item.strip()]
    return [item.lower() for item in _read_values(Path.home() / ".config" / "nhlv" / "config", "favorite_players")]
