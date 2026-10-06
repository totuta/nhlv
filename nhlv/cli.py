"""Command-line interface for nhlv."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .api import NHLAPIError, NHLClient, valid_date
from .config import favorite_players, favorite_teams
from .formatting import (
    format_boxscore,
    format_favorite_player_stats,
    format_leaders,
    format_schedule,
    format_scores,
    format_standings,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NHL scores, standings, and schedules")
    parser.add_argument("--version", action="version", version=f"nhlv {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    for command, help_text in (("scores", "show scores"), ("schedule", "show the schedule")):
        sub = subparsers.add_parser(command, help=help_text)
        sub.add_argument("--date", default="now", type=valid_date, help="YYYY-MM-DD (default: now)")
        sub.add_argument("--team", metavar="TEAM", help="filter by team abbreviation, e.g. TOR")
    standings = subparsers.add_parser("standings", help="show league standings")
    standings.add_argument(
        "category",
        nargs="?",
        choices=("division", "wildcard"),
        default="division",
        help="standings view (default: division)",
    )
    standings.add_argument("--date", default="now", type=valid_date, help="YYYY-MM-DD (default: now)")
    standings.add_argument("--group", help="filter by division or conference")
    team = subparsers.add_parser("team", help="show a team's season schedule")
    team.add_argument("team", metavar="TEAM", help="three-letter team abbreviation, e.g. TOR")
    leaders = subparsers.add_parser("leaders", help="show statistical leaders")
    leaders.add_argument("player_type", choices=("skaters", "goalies"), nargs="?", default="skaters")
    leaders.add_argument("--category", default=None, help="stat category (default: points or wins)")
    leaders.add_argument("--limit", type=int, default=10, choices=range(1, 101))
    boxscore = subparsers.add_parser("boxscore", help="show a game boxscore")
    boxscore.add_argument("game_id", nargs="?", help="NHL game ID")
    boxscore.add_argument("--team", help="find today's game for this team")
    boxscore.add_argument("--favorites", action="store_true", help="show today's games for favourite teams")
    boxscore.add_argument("--date", default="now", type=valid_date, help="YYYY-MM-DD or yesterday")
    favorite_stats = subparsers.add_parser("favorite-stats", help="show favourite player stats")
    favorite_stats.add_argument("--date", default="now", type=valid_date, help="YYYY-MM-DD or yesterday")
    return parser


def run(args: argparse.Namespace, client: NHLClient) -> str:
    if args.command in (None, "scores"):
        return format_scores(client.scores(getattr(args, "date", "now")), getattr(args, "team", None), favorite_teams())
    if args.command == "standings":
        return format_standings(client.standings(args.date), args.group, args.category, favorite_teams())
    if args.command == "schedule":
        return format_schedule(client.schedule(args.date), args.team, favorite_teams())
    if args.command == "team":
        return format_schedule(client.team_schedule(args.team), args.team)
    if args.command == "leaders":
        category = args.category or ("points" if args.player_type == "skaters" else "wins")
        return format_leaders(client.leaders(args.player_type, category, args.limit), category, args.player_type)
    if args.command == "boxscore":
        favorites = favorite_teams()
        team = args.team
        if args.favorites:
            team = None
        if args.game_id:
            return format_boxscore(client.boxscore(args.game_id), favorites, favorite_players())
        if not args.favorites and not team:
            raise ValueError("provide GAME_ID, --team TEAM, or --favorites")
        games = client.scores(args.date).get("games", [])
        targets = set(favorites if args.favorites else [team.upper()])
        selected = [game for game in games if targets.intersection({game.get("awayTeam", {}).get("abbrev", "").upper(), game.get("homeTeam", {}).get("abbrev", "").upper()})]
        if not selected:
            raise ValueError("no matching game found today")
        return "\n\n".join(
            format_boxscore(client.boxscore(game["id"]), favorites, favorite_players()) for game in selected
        )
    if args.command == "favorite-stats":
        players = favorite_players()
        if not players:
            raise ValueError("no favourite players configured")
        payload = client.scores(args.date)
        game_payloads = [client.boxscore(game["id"]) for game in payload.get("games", [])]
        return format_favorite_player_stats(game_payloads, players)
    raise ValueError(f"unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(run(args, NHLClient()))
    except (NHLAPIError, ValueError) as exc:
        print(f"nhlv: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
