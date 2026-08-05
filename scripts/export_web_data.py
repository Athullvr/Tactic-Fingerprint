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

EXPLAINED_FEATURES = {
    "possession_share": "possession control",
    "avg_pass_length": "passing distance",
    "forward_pass_ratio": "forward intent",
    "long_pass_ratio": "directness",
    "avg_action_height": "defensive height",
    "width_dispersion": "width",
}


def value(row: pd.Series, feature: str) -> float:
    return float(row.get(f"{feature}_mean", row.get(feature, 0.0)))


def archetype(row: pd.Series, peers: pd.DataFrame) -> tuple[str, str]:
    """Return a transparent, peer-relative style label."""
    possession = value(row, "possession_share")
    direct = value(row, "long_pass_ratio")
    height = value(row, "avg_action_height")
    width = value(row, "width_dispersion")
    if possession >= peers["possession_share_mean"].quantile(0.75) and height >= peers["avg_action_height_mean"].quantile(0.60):
        return "High-control press", "Keeps the ball and operates higher up the pitch than most peers."
    if direct >= peers["long_pass_ratio_mean"].quantile(0.75):
        return "Direct transition", "Moves play forward with a comparatively direct passing mix."
    if width >= peers["width_dispersion_mean"].quantile(0.75):
        return "Wide progression", "Distributes actions broadly across the pitch width."
    if height <= peers["avg_action_height_mean"].quantile(0.25):
        return "Low territorial block", "Defensive actions are concentrated deeper than most peers."
    return "Balanced system", "No single style dimension dominates this team’s tactical profile."


def similarity_reasons(row: pd.Series, other: pd.Series, peers: pd.DataFrame) -> list[str]:
    """Explain nearest-neighbour results using the closest tactical dimensions."""
    differences = []
    for feature, label in EXPLAINED_FEATURES.items():
        spread = float(peers[f"{feature}_mean"].max() - peers[f"{feature}_mean"].min()) or 1.0
        differences.append((abs(value(row, feature) - value(other, feature)) / spread, label))
    return [label for _, label in sorted(differences)[:2]]


def export_web_data(signature_path: Path, output_path: Path) -> None:
    """Turn a signature table into the static payload consumed by the website."""
    table = pd.read_parquet(signature_path)
    profiles = []
    for _, row in table.iterrows():
        team = str(row["team"])
        competition = str(row.get("competition", "StatsBomb Open Data"))
        season = str(row.get("season", ""))
        signature = {key: value.item() if hasattr(value, "item") else value for key, value in row.items()}
        zones = [
            {"length": length, "width": width, "value": float(row.get(f"{zone_column(length, width)}_mean", row.get(zone_column(length, width), 0.0)))}
            for width in range(5)
            for length in range(6)
        ]
        peers = table.loc[(table.get("competition", competition) == competition) & (table.get("season", season).astype(str) == season)]
        similar = []
        for item in most_similar_teams(team, peers, top_n=5).to_dict(orient="records"):
            other = peers.loc[peers["team"].astype(str) == str(item["team"])].iloc[0]
            similar.append({**item, "reasons": similarity_reasons(row, other, peers)})
        style, style_reason = archetype(row, peers)
        matches_played = int(row.get("matches_played", 0))
        profiles.append({
            "id": f"{competition}|{season}|{team}",
            "team": team,
            "competition": competition,
            "season": season,
            "signature": signature,
            "zones": zones,
            "similar": similar,
            "archetype": style,
            "archetype_reason": style_reason,
            "data_quality": {
                "matches_played": matches_played,
                "label": "Strong sample" if matches_played >= 8 else "Developing sample" if matches_played >= 4 else "Small sample",
            },
        })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sources = sorted({(profile["competition"], profile["season"]) for profile in profiles})
    output_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [{"competition": competition, "season": season} for competition, season in sources],
        "teams": profiles,
    }, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    export_web_data(Path("data/processed/team_signatures.parquet"), Path("web/public/data/tactical.json"))
