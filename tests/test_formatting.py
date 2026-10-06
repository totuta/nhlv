from nhlv.formatting import format_scores, format_standings


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
