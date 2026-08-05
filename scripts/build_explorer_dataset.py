"""Build one deployable dataset from several StatsBomb Open Data sources."""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.export_web_data import export_web_data
from src.data.cleaner import clean_events
from src.data.loader import load_cached_events
from src.features.build_signature import aggregate_season_signatures, build_match_signatures


# Add sources here as coverage grows.  The Bundesliga sample supplies 18 clubs,
# while the Champions League sample retains the project's original comparison.
SOURCES = [
    ("1. Bundesliga", 2023),
    ("Champions League", 2015),
]


def main() -> None:
    tables: list[pd.DataFrame] = []
    match_tables: list[pd.DataFrame] = []
    for competition, season in SOURCES:
        raw = load_cached_events(competition, season)
        matches = build_match_signatures(clean_events(raw))
        signatures = aggregate_season_signatures(matches)
        signatures.insert(1, "competition", competition)
        signatures.insert(2, "season", season)
        matches.insert(2, "competition", competition)
        matches.insert(3, "season", season)
        tables.append(signatures)
        match_tables.append(matches)
        print(f"Built {len(signatures)} team profiles for {competition} {season}.")

    combined = pd.concat(tables, ignore_index=True)
    output = Path("data/processed/explorer_signatures.parquet")
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output, index=False)
    export_web_data(output, Path("web/public/data/tactical.json"), pd.concat(match_tables, ignore_index=True))
    print(f"Published {len(combined)} total profiles to web/public/data/tactical.json")


if __name__ == "__main__":
    main()
