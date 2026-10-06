# nhlv

`nhlv` is a small command-line client for NHL scores, standings, and schedules.
It uses the public NHL web API and does not require an account or subscription.

## Install

With `pipx`:

```bash
pipx install git+https://github.com/totuta/nhlv.git
```

With a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

## Usage

```bash
nhlv                         # today's scores
nhlv scores --team TOR       # today's Toronto games
nhlv standings               # current standings
nhlv standings --group East  # filter by conference/division name
nhlv schedule                # upcoming schedule
nhlv schedule --team MTL    # upcoming Montreal schedule
nhlv team TOR                # Toronto season schedule
nhlv scores --date 2026-10-05
```

The default output is plain text so it works well in a terminal, `less`,
scripts, and SSH sessions.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```

The project is independent of `mlbv`; it only shares the same general goal of
providing a lightweight terminal sports client.

## Data source

Data is retrieved from NHL's public web endpoints under
`https://api-web.nhle.com/v1`. The endpoints are not an official stable SDK
contract, so API changes may require updates to this project.

## License

MIT
