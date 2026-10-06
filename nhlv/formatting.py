"""Human-readable terminal formatting for NHL API payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

DIVISION_ORDER = ("Atlantic", "Metropolitan", "Central", "Pacific")


def text(value: Any, fallback: str = "-") -> str:
    if isinstance(value, dict):
        return str(value.get("default") or next(iter(value.values()), fallback))
    return fallback if value is None or value == "" else str(value)


def team_name(team: dict[str, Any]) -> str:
    for key in ("teamName", "name", "placeName", "abbrev"):
        value = team.get(key)
        if value:
            return text(value)
    return "-"


def heading(title: str) -> str:
    return f"\n{title}\n{'=' * len(title)}"


def game_rows(payload: dict[str, Any], team_filter: str | None = None) -> list[str]:
    target = team_filter.upper() if team_filter else None
    rows = []
    for game in payload.get("games", []):
        away = game.get("awayTeam", {})
        home = game.get("homeTeam", {})
        away_code = text(away.get("abbrev"), "???")
        home_code = text(home.get("abbrev"), "???")
        if target and target not in {away_code.upper(), home_code.upper()}:
            continue
        state = text(game.get("gameState") or game.get("gameScheduleState"), "-")
        away_score = away.get("score", "-")
        home_score = home.get("score", "-")
        start = game.get("startTimeUTC")
        if start and state in {"FUT", "PRE"}:
            try:
                start = datetime.fromisoformat(start.replace("Z", "+00:00")).astimezone().strftime("%H:%M")
            except ValueError:
                start = "-"
        else:
            start = text(game.get("gameOutcome", {}).get("lastPeriodType"), "-")
        rows.append(f"{start:>5}  {away_code:>3} {away_score:>2}  @  {home_code:<3} {home_score:>2}  {state}")
    return rows


def format_scores(payload: dict[str, Any], team_filter: str | None = None) -> str:
    game_day = text(payload.get("gameWeekDate") or payload.get("currentDate") or payload.get("date"), "today")
    rows = game_rows(payload, team_filter)
    return heading(f"NHL Scores: {game_day}") + ("\n" + "\n".join(rows) if rows else "\nNo games found.")


def _standings_rows(payload: dict[str, Any], group: str | None = None) -> list[tuple[str, dict[str, Any]]]:
    selected = []
    needle = group.lower() if group else None
    for record in payload.get("standings", []):
        division = text(record.get("divisionName"), "-")
        conference = text(record.get("conferenceName"), "-")
        if needle and needle not in division.lower() and needle not in conference.lower():
            continue
        selected.append((division, record))

    division_rank = {name: index for index, name in enumerate(DIVISION_ORDER)}
    return sorted(
        selected,
        key=lambda item: (
            division_rank.get(item[0], len(DIVISION_ORDER)),
            int(item[1].get("divisionSequence") or item[1].get("leagueSequence") or 999),
        ),
    )


def format_standings(payload: dict[str, Any], group: str | None = None) -> str:
    rows = []
    current_group = None
    for division, record in _standings_rows(payload, group):
        if division != current_group:
            rows.extend((f"\n{division}", " RK  TEAM                         GP   W   L OT  PTS  DIFF"))
            current_group = division
        name = team_name(record)
        rank = text(record.get("divisionSequence") or record.get("leagueSequence"), "-")
        rows.append(
            f"{rank:>3}  {name:<28} {record.get('gamesPlayed', '-'):>2}"
            f" {record.get('wins', '-'):>3} {record.get('losses', '-'):>3}"
            f" {record.get('otLosses', '-'):>2} {record.get('points', '-'):>4}"
            f" {record.get('goalDifferential', '-'):>5}"
        )
    return heading("NHL Standings") + ("\n" + "\n".join(rows) if rows else "\nNo standings found.")


def format_schedule(payload: dict[str, Any], team_filter: str | None = None) -> str:
    rows = []
    weeks = payload.get("gameWeek", [])
    if payload.get("games"):
        weeks = [{"date": payload.get("currentDate") or payload.get("date"), "games": payload["games"]}]
    for week in weeks:
        date_value = text(week.get("date"), "-")
        game_lines = game_rows({"games": week.get("games", [])}, team_filter)
        if game_lines:
            rows.append(f"\n{date_value}")
            rows.extend(game_lines)
    return heading("NHL Schedule") + ("\n" + "\n".join(rows) if rows else "\nNo games found.")
