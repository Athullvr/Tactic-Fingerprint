"""Download StatsBomb Open Data into the ignored local cache."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.loader import download_competition


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--competition", default="Champions League")
    parser.add_argument("--season", type=int, default=2015)
    args = parser.parse_args()
    print(f"Cached raw events in {download_competition(args.competition, args.season)}")


if __name__ == "__main__":
    main()
