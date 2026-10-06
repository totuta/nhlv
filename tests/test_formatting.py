from nhlv.formatting import format_boxscore, format_favorite_player_stats, format_schedule, format_scores, format_standings
from nhlv.api import valid_date


def test_valid_date_supports_yesterday():
    assert len(valid_date("yesterday")) == 10
    assert valid_date("now") == "now"


def test_format_scores_filters_team():
    payload = {
        "gameWeekDate": "2026-10-05",
        "games": [
            {"gameState": "FINAL", "awayTeam": {"abbrev": "TOR", "score": 3}, "homeTeam": {"abbrev": "MTL", "score": 2}},
            {"gameState": "FUT", "awayTeam": {"abbrev": "BOS", "score": 0}, "homeTeam": {"abbrev": "NYR", "score": 0}},
        ],
    }
    output = format_scores(payload, "TOR")
    assert "TOR" in output
    assert "BOS" not in output


def test_format_schedule_highlights_favorite_team():
    payload = {
        "currentDate": "2026-10-05",
        "games": [
            {"gameState": "FINAL", "awayTeam": {"abbrev": "MTL", "score": 3}, "homeTeam": {"abbrev": "TOR", "score": 2}},
            {"gameState": "FINAL", "awayTeam": {"abbrev": "BOS", "score": 1}, "homeTeam": {"abbrev": "NYR", "score": 0}},
        ],
    }
    output = format_schedule(payload, favorites=["TOR"])
    assert "\033[94m" in output
    assert output.count("\033[94m") == 1


def test_format_standings():
    payload = {"standings": [{
        "divisionName": "Atlantic",
        "teamName": {"default": "Toronto Maple Leafs"},
        "divisionSequence": 1,
        "gamesPlayed": 10,
        "wins": 7,
        "losses": 2,
        "otLosses": 1,
        "points": 15,
        "goalDifferential": 8,
    }]}
    output = format_standings(payload)
    assert "Atlantic" in output
    assert "Toronto Maple Leafs" in output
    assert "15" in output


def test_format_standings_groups_and_sorts_divisions():
    payload = {"standings": [
        {"divisionName": "Pacific", "teamName": {"default": "Pacific Team"}, "divisionSequence": 2},
        {"divisionName": "Atlantic", "teamName": {"default": "Atlantic Team"}, "divisionSequence": 2},
        {"divisionName": "Pacific", "teamName": {"default": "Pacific Leader"}, "divisionSequence": 1},
    ]}
    output = format_standings(payload)
    assert output.index("Atlantic") < output.index("Pacific")
    assert output.index("Pacific Leader") < output.index("Pacific Team")


def test_format_wildcard_standings():
    payload = {"standings": [
        {"conferenceName": "Eastern", "divisionName": "Atlantic", "divisionSequence": 4, "wildcardSequence": 2, "teamName": {"default": "East Two"}},
        {"conferenceName": "Eastern", "divisionName": "Metropolitan", "divisionSequence": 4, "wildcardSequence": 1, "teamName": {"default": "East One"}},
        {"conferenceName": "Eastern", "divisionName": "Atlantic", "divisionSequence": 1, "wildcardSequence": 0, "teamName": {"default": "Division Leader"}},
    ]}
    output = format_standings(payload, category="wildcard")
    assert "WC1" in output
    assert output.index("East One") < output.index("East Two")
    assert "Division Leader" not in output


def test_format_boxscore_highlights_favorite_team():
    payload = {
        "id": 123,
        "awayTeam": {"abbrev": "TOR", "placeName": {"default": "Toronto"}, "score": 3},
        "homeTeam": {"abbrev": "MTL", "placeName": {"default": "Montreal"}, "score": 2},
        "playerByGameStats": {
            "awayTeam": {"forwards": [{"name": {"default": "A. Player"}, "goals": 1, "assists": 0, "points": 1}], "goalies": []},
            "homeTeam": {"forwards": [], "goalies": [{"name": {"default": "H. Goalie"}, "saves": 25, "shotsAgainst": 27, "goalsAgainst": 2, "toi": "60:00"}]},
        },
    }
    output = format_boxscore(payload, ["MTL"], ["player"])
    assert "Toronto" in output
    assert "\033[94m" in output
    assert "skaters" in output
    assert "goalies" in output
    assert "0.926" in output


def test_format_favorite_player_stats():
    payload = {
        "id": 123,
        "awayTeam": {"abbrev": "MTL"},
        "homeTeam": {"abbrev": "TOR"},
        "playerByGameStats": {
            "awayTeam": {"forwards": [{"name": {"default": "L. Hutson"}, "goals": 1, "assists": 2, "points": 3, "plusMinus": 2, "sog": 4, "pim": 0, "toi": "22:10"}]},
            "homeTeam": {"forwards": [], "goalies": [{"name": {"default": "I. Goalie"}, "saves": 28, "shotsAgainst": 30, "goalsAgainst": 2, "toi": "60:00"}]},
        },
    }
    output = format_favorite_player_stats([payload], ["hutson", "goalie"])
    assert "L. Hutson" in output
    assert "22:10" in output
    assert "Skaters" in output
    assert "Goalies" in output
    assert "28" in output
    assert "0.933" in output


def test_favorite_player_matching_requires_exact_last_name():
    payload = {
        "id": 123,
        "awayTeam": {"abbrev": "MTL"},
        "homeTeam": {"abbrev": "TOR"},
        "playerByGameStats": {
            "awayTeam": {"forwards": [{"name": {"default": "A. DeSmith"}}]},
            "homeTeam": {"forwards": [{"name": {"default": "J. Smith"}}]},
        },
    }
    output = format_favorite_player_stats([payload], ["smith"])
    assert "J. Smith" in output
    assert "A. DeSmith" not in output
