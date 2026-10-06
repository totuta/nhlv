"""Small client for the public NHL web API."""

from __future__ import annotations

from datetime import date
from typing import Any

import requests

BASE_URL = "https://api-web.nhle.com/v1"


class NHLAPIError(RuntimeError):
    """Raised when the NHL API cannot provide a usable response."""


class NHLClient:
    def __init__(self, timeout: float = 15.0, session: requests.Session | None = None) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", "nhlv/0.1.0")

    def get(self, path: str) -> dict[str, Any]:
        url = f"{BASE_URL}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise NHLAPIError(f"NHL API request failed: {exc}") from exc
        except ValueError as exc:
            raise NHLAPIError("NHL API returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise NHLAPIError("NHL API returned an unexpected response")
        return payload

    def scores(self, day: str = "now") -> dict[str, Any]:
        return self.get(f"score/{day}")

    def standings(self, day: str = "now") -> dict[str, Any]:
        return self.get(f"standings/{day}")

    def schedule(self, day: str = "now") -> dict[str, Any]:
        return self.get(f"schedule/{day}")

    def team_schedule(self, team: str, day: str = "now") -> dict[str, Any]:
        return self.get(f"club-schedule-season/{team.upper()}/{day}")


def valid_date(value: str) -> str:
    if value == "now":
        return value
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid date: {value}; use YYYY-MM-DD") from exc
    return value
