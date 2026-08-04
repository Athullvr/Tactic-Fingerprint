"""Export derived tactical signatures as a static web dataset.

This file is safe to deploy: it contains only aggregate team metrics and never
includes raw StatsBomb events.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analysis.similarity import most_similar_teams
from src.features.spatial import zone_column


def export_web_data(signature_path: Path, output_path: Path) -> None:
    """Turn a signature table into the static payload consumed by the website."""
    table = pd.read_parquet(signature_path)
    profiles = []
    for _, row in table.iterrows():
        team = str(row["team"])
        signature = {key: value.item() if hasattr(value, "item") else value for key, value in row.items()}
        zones = [
            {"length": length, "width": width, "value": float(row.get(f"{zone_column(length, width)}_mean", row.get(zone_column(length, width), 0.0)))}
            for width in range(5)
            for length in range(6)
        ]
        profiles.append({"team": team, "signature": signature, "zones": zones, "similar": most_similar_teams(team, table, top_n=5).to_dict(orient="records")})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "teams": profiles}, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    export_web_data(Path("data/processed/team_signatures.parquet"), Path("web/public/data/tactical.json"))
