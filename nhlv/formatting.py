"""Human-readable terminal formatting for NHL API payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

DIVISION_ORDER = ("Atlantic", "Metropolitan", "Central", "Pacific")
CONFERENCE_ORDER = ("Eastern", "Western")
FAVORITE_COLOR = "\033[94m"
RESET_COLOR = "\033[0m"


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
    return f"\n   {'═' * 8} {title} {'═' * 8}"


def game_rows(
    payload: dict[str, Any], team_filter: str | None = None, favorites: Iterable[str] = ()
) -> list[str]:
    target = team_filter.upper() if team_filter else None
    favorite_set = {team.upper() for team in favorites}
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
        row = f"{start:>5}  {away_code:>3} {away_score:>2}  @  {home_code:<3} {home_score:>2}  {state}"
        rows.append(f"{FAVORITE_COLOR}{row}{RESET_COLOR}" if {away_code.upper(), home_code.upper()} & favorite_set else row)
    return rows


def format_scores(payload: dict[str, Any], team_filter: str | None = None, favorites: Iterable[str] = ()) -> str:
    game_day = text(payload.get("gameWeekDate") or payload.get("currentDate") or payload.get("date"), "today")
    rows = game_rows(payload, team_filter, favorites)
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


def _standing_line(record: dict[str, Any], rank: str, favorites: Iterable[str] = ()) -> str:
    name = team_name(record)
    line = (
        f"{rank:>3}  {name:<28} {record.get('gamesPlayed', '-'):>2}"
        f" {record.get('wins', '-'):>3} {record.get('losses', '-'):>3}"
        f" {record.get('otLosses', '-'):>2} {record.get('points', '-'):>4}"
        f" {record.get('goalDifferential', '-'):>5}"
    )
    favorite_set = {team.upper() for team in favorites}
    team_code = text(record.get("teamAbbrev"), "").upper()
    return f"{FAVORITE_COLOR}{line}{RESET_COLOR}" if team_code in favorite_set else line


def _standing_header() -> str:
    return f"{'RK':>3}  {'TEAM':<28} {'GP':>2} {'W':>3} {'L':>3} {'OT':>2} {'PTS':>4} {'DIFF':>5}"


def format_standings(
    payload: dict[str, Any], group: str | None = None, category: str = "division", favorites: Iterable[str] = ()
) -> str:
    if category == "wildcard":
        return format_wildcard_standings(payload, group, favorites)

    rows = []
    current_group = None
    for division, record in _standings_rows(payload, group):
        if division != current_group:
            rows.extend((f"\n   ─── {division} ─────────────────────────────", _standing_header()))
            current_group = division
        rank = text(record.get("divisionSequence") or record.get("leagueSequence"), "-")
        rows.append(_standing_line(record, rank, favorites))
    return heading("NHL Standings") + ("\n" + "\n".join(rows) if rows else "\nNo standings found.")


def format_wildcard_standings(payload: dict[str, Any], group: str | None = None, favorites: Iterable[str] = ()) -> str:
    """Display the standard two wild-card spots and the remaining race."""
    conferences: dict[str, list[dict[str, Any]]] = {name: [] for name in CONFERENCE_ORDER}
    needle = group.lower() if group else None
    for record in payload.get("standings", []):
        conference = text(record.get("conferenceName"), "-")
        division = text(record.get("divisionName"), "-")
        if record.get("divisionSequence", 999) <= 3:
            continue
        if needle and needle not in conference.lower() and needle not in division.lower():
            continue
        if conference in conferences:
            conferences[conference].append(record)

    rows = []
    for conference in CONFERENCE_ORDER:
        records = sorted(
            conferences[conference],
            key=lambda record: int(record.get("wildcardSequence") or 999),
        )
        if not records:
            continue
        rows.append(f"\n   ─── {conference} Conference ─────────────────────")
        rows.append(_standing_header())
        for index, record in enumerate(records, start=1):
            rank = f"WC{index}" if index <= 2 else str(index)
            rows.append(_standing_line(record, rank, favorites))
    return heading("NHL Wild Card Standings") + ("\n" + "\n".join(rows) if rows else "\nNo wild card standings found.")


def format_schedule(
    payload: dict[str, Any],
    team_filter: str | None = None,
    favorites: Iterable[str] = (),
) -> str:
    rows = []
    weeks = payload.get("gameWeek", [])
    if payload.get("games"):
        weeks = [{"date": payload.get("currentDate") or payload.get("date"), "games": payload["games"]}]
    for week in weeks:
        date_value = text(week.get("date"), "-")
        game_lines = game_rows({"games": week.get("games", [])}, team_filter, favorites)
        if game_lines:
            rows.append(f"\n{date_value}")
            rows.extend(game_lines)
    return heading("NHL Schedule") + ("\n" + "\n".join(rows) if rows else "\nNo games found.")


def _player_name(player: dict[str, Any]) -> str:
    name = player.get("name") or {}
    return text(name, f"{text(player.get('firstName'))} {text(player.get('lastName'))}")


def _favorite_player_matches(player_name: str, favorite_players: Iterable[str]) -> bool:
    """Match configured last names exactly against the player's last name."""
    name_parts = player_name.strip().split()
    if not name_parts:
        return False
    last_name = name_parts[-1].strip(".,").casefold()
    return last_name in {favorite.strip().strip(".,").casefold() for favorite in favorite_players}


def format_leaders(payload: dict[str, Any], category: str, player_type: str) -> str:
    entries = payload.get(category, [])
    title = f"NHL {player_type.title()} Leaders: {category}"
    rows = ["   RK  PLAYER                         TEAM  VALUE"]
    for index, player in enumerate(entries, start=1):
        rows.append(f"{index:>5}  {_player_name(player):<29} {text(player.get('teamAbbrev'), '---'):>3}  {text(player.get('value'), '-')}")
    return heading(title) + ("\n" + "\n".join(rows) if entries else "\nNo leaders found.")


def _boxscore_team_name(team: dict[str, Any]) -> str:
    return f"{text(team.get('abbrev'), '---')} {text(team.get('placeName'))}"


def _boxscore_players(section: dict[str, Any]) -> list[dict[str, Any]]:
    players = []
    for group in ("forwards", "defense", "goalies"):
        players.extend(section.get(group, []))
    return players


def format_boxscore(
    payload: dict[str, Any],
    favorites: Iterable[str] = (),
    favorite_players: Iterable[str] = (),
) -> str:
    favorite_set = {team.upper() for team in favorites}
    favorite_player_set = {player.lower() for player in favorite_players}
    away = payload.get("awayTeam", {})
    home = payload.get("homeTeam", {})
    rows = [heading(f"NHL Boxscore: {payload.get('id', '-')}")]
    rows.append(f"{_boxscore_team_name(away)} {away.get('score', '-')}  @  {_boxscore_team_name(home)} {home.get('score', '-')}")
    stats = payload.get("playerByGameStats", {})
    for side, team in (("awayTeam", away), ("homeTeam", home)):
        code = text(team.get("abbrev"), "---").upper()
        label = f"{_boxscore_team_name(team)}"
        if code in favorite_set:
            label = f"{FAVORITE_COLOR}{label}{RESET_COLOR}"
        team_stats = stats.get(side, {})
        rows.extend((f"\n{label} skaters", " PLAYER                 G A P +/- SOG PIM TOI"))
        for player in team_stats.get("forwards", []) + team_stats.get("defense", []):
            player_name = text(player.get("name"), "-")
            line = f" {player_name:<22} {player.get('goals', 0):>1} {player.get('assists', 0):>1} {player.get('points', 0):>1} {player.get('plusMinus', 0):>3} {player.get('sog', 0):>3} {player.get('pim', 0):>3} {text(player.get('toi'), '-'):>4}"
            player_matches = _favorite_player_matches(player_name, favorite_player_set)
            rows.append(f"{FAVORITE_COLOR}{line}{RESET_COLOR}" if player_matches else line)
        goalies = team_stats.get("goalies", [])
        if goalies:
            rows.extend((f"\n{label} goalies", " GOALIE                 SV  SA  GA   SV%   TOI"))
            for player in goalies:
                player_name = text(player.get("name"), "-")
                saves = player.get("saves", player.get("sv", 0))
                shots = player.get("shotsAgainst", player.get("shots", 0))
                goals_against = player.get("goalsAgainst", player.get("ga", 0))
                save_pct = player.get("savePctg", player.get("savePercentage"))
                if save_pct is None and shots:
                    save_pct = (int(saves) / int(shots)) if int(shots) else 0
                save_pct_text = f"{float(save_pct):.3f}" if save_pct is not None else "-"
                line = (
                    f" {player_name:<22} {saves:>3} {shots:>3} {goals_against:>3}"
                    f" {save_pct_text:>6} {text(player.get('toi'), '-'):>5}"
                )
                player_matches = any(last_name in player_name.lower() for last_name in favorite_player_set)
                rows.append(f"{FAVORITE_COLOR}{line}{RESET_COLOR}" if player_matches else line)
    return "\n".join(rows)


def format_favorite_player_stats(
    payloads: Iterable[dict[str, Any]], favorite_players: Iterable[str]
) -> str:
    """Display today's favourite skaters and goalies in separate tables."""
    player_names = {player.lower() for player in favorite_players}
    skaters: list[dict[str, Any]] = []
    goalies: list[dict[str, Any]] = []
    for payload in payloads:
        game_id = payload.get("id", "-")
        stats = payload.get("playerByGameStats", {})
        for side in ("awayTeam", "homeTeam"):
            team = payload.get(side, {})
            team_code = text(team.get("abbrev"), "---")
            team_stats = stats.get(side, {})
            for player in team_stats.get("forwards", []) + team_stats.get("defense", []):
                name = text(player.get("name"), "-")
                if not _favorite_player_matches(name, player_names):
                    continue
                skaters.append({**player, "game": game_id, "team": team_code, "name": name})
            for player in team_stats.get("goalies", []):
                name = text(player.get("name"), "-")
                if not _favorite_player_matches(name, player_names):
                    continue
                goalies.append({**player, "game": game_id, "team": team_code, "name": name})

    rows = [heading("NHL Favourite Player Stats")]
    if skaters:
        rows.extend(("\nSkaters", " TEAM  PLAYER                 G  A  P +/- SOG PIM   TOI"))
        for player in skaters:
            rows.append(
                f" {player['team']:<5} {player['name']:<22}"
                f" {player.get('goals', 0):>2} {player.get('assists', 0):>2} {player.get('points', 0):>2}"
                f" {player.get('plusMinus', 0):>3} {player.get('sog', 0):>3} {player.get('pim', 0):>3}"
                f" {text(player.get('toi'), '-'):>5}"
            )
    if goalies:
        rows.extend(("\nGoalies", " TEAM  PLAYER                 SV  SA  GA   SV%   TOI"))
        for player in goalies:
            saves = player.get("saves", player.get("sv", 0))
            shots = player.get("shotsAgainst", player.get("shots", 0))
            goals_against = player.get("goalsAgainst", player.get("ga", 0))
            save_pct = player.get("savePctg", player.get("savePercentage"))
            if save_pct is None and shots:
                save_pct = (int(saves) / int(shots)) if int(shots) else 0
            save_pct_text = f"{float(save_pct):.3f}" if save_pct is not None else "-"
            rows.append(
                f" {player['team']:<5} {player['name']:<22}"
                f" {saves:>2} {shots:>3} {goals_against:>3} {save_pct_text:>6}"
                f" {text(player.get('toi'), '-'):>5}"
            )
    if not skaters and not goalies:
        rows.append("\nNo favourite player stats found.")
    return "\n".join(rows)
