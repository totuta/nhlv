"""Command-line interface for nhlv."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .api import NHLAPIError, NHLClient, valid_date
from .formatting import format_schedule, format_scores, format_standings


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
    return parser


def run(args: argparse.Namespace, client: NHLClient) -> str:
    if args.command in (None, "scores"):
        return format_scores(client.scores(getattr(args, "date", "now")), getattr(args, "team", None))
    if args.command == "standings":
        return format_standings(client.standings(args.date), args.group, args.category)
    if args.command == "schedule":
        return format_schedule(client.schedule(args.date), args.team)
    if args.command == "team":
        return format_schedule(client.team_schedule(args.team), args.team)
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
