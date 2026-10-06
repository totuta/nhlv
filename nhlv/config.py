"""Local nhlv preferences, including favourite teams."""

from __future__ import annotations

import os
from pathlib import Path


def _read_favs(path: Path) -> list[str]:
    if not path.is_file():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("favs="):
            return [item.strip().upper() for item in line[5:].split(",") if item.strip()]
    return []


def favorite_teams() -> list[str]:
    """Read NHLV_FAVORITES, nhlv config, then the existing mlbv config."""
    env_value = os.environ.get("NHLV_FAVORITES", "")
    if env_value:
        return [item.strip().upper() for item in env_value.split(",") if item.strip()]
    home = Path.home()
    return _read_favs(home / ".config" / "nhlv" / "config") or _read_favs(home / ".config" / "mlbv" / "config")
