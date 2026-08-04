"""Run the raw-events-to-tactical-signatures pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analysis.clustering import cluster_teams
from src.analysis.embedding import pca_embedding
from src.data.cleaner import clean_events
from src.data.loader import load_cached_events
from src.features.build_signature import build_signatures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--competition", default="Champions League")
    parser.add_argument("--season", type=int, default=2015)
    parser.add_argument("--mode", choices=["season", "per-match"], default="season")
    parser.add_argument("--no-download", action="store_true", help="Fail if a local raw cache is missing.")
    args = parser.parse_args()
    raw = load_cached_events(args.competition, args.season, download_missing=not args.no_download)
    clean = clean_events(raw)
    output = Path("data/processed") / ("team_signatures.parquet" if args.mode == "season" else "match_signatures.parquet")
    signatures = build_signatures(clean, mode=args.mode, output_path=output)
    print(f"Saved {len(signatures)} {args.mode} signatures to {output}")
    if len(signatures) >= 3:
        embedding, variance = pca_embedding(signatures)
        members, _ = cluster_teams(signatures)
        print(f"PCA explained variance: {sum(variance):.1%}")
        print(members.to_string(index=False))


if __name__ == "__main__":
    main()
