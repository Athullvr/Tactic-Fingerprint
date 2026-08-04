"""FastAPI service for the Tactic Fingerprint web experience.

The API only reads derived signature files. Raw StatsBomb data remains local and
is never exposed by this service.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.analysis.clustering import cluster_teams
from src.analysis.embedding import pca_embedding
from src.analysis.similarity import most_similar_teams
from src.features.spatial import zone_column

ROOT = Path(__file__).resolve().parents[2]
SIGNATURE_PATH = ROOT / "data/processed/team_signatures.parquet"

app = FastAPI(title="Tactic Fingerprint API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def signatures() -> pd.DataFrame:
    """Load the compact, derived team-signature table."""
    if not SIGNATURE_PATH.exists():
        raise FileNotFoundError("Run scripts/run_pipeline.py before starting the API.")
    return pd.read_parquet(SIGNATURE_PATH)


def record(row: pd.Series) -> dict[str, Any]:
    """Convert a pandas row into JSON-safe primitives."""
    return {key: value.item() if hasattr(value, "item") else value for key, value in row.items()}


def team_row(team: str) -> pd.Series:
    table = signatures()
    match = table.loc[table.team == team]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Unknown team: {team}")
    return match.iloc[0]


@app.get("/health")
def health() -> dict[str, Any]:
    """Report API readiness without exposing event data."""
    try:
        return {"status": "ready", "teams": len(signatures())}
    except FileNotFoundError as error:
        return {"status": "needs_pipeline", "detail": str(error)}


@app.get("/teams")
def teams() -> list[str]:
    """List available team names."""
    return sorted(signatures().team.astype(str).tolist())


@app.get("/teams/{team}")
def team(team: str) -> dict[str, Any]:
    """Return a full fingerprint, spatial grid, and nearest tactical neighbours."""
    row = team_row(team)
    table = signatures()
    zones = [
        {"length": length, "width": width, "value": float(row.get(f"{zone_column(length, width)}_mean", row.get(zone_column(length, width), 0.0)))}
        for width in range(5)
        for length in range(6)
    ]
    return {
        "team": team,
        "signature": record(row),
        "zones": zones,
        "similar": most_similar_teams(team, table, top_n=5).to_dict(orient="records"),
    }


@app.get("/compare")
def compare(team_a: str, team_b: str) -> dict[str, Any]:
    """Return two named profiles for a direct client-side comparison."""
    return {"left": record(team_row(team_a)), "right": record(team_row(team_b))}


@app.get("/embedding")
def embedding() -> dict[str, Any]:
    """Return PCA coordinates and descriptive style-cluster membership."""
    table = signatures()
    points, variance = pca_embedding(table)
    members, centroids = cluster_teams(table)
    merged = points.merge(members, on="team", how="left")
    return {
        "variance": variance,
        "points": merged.to_dict(orient="records"),
        "clusters": centroids.to_dict(orient="records"),
    }
