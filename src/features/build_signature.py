"""Assemble tactical DNA signature tables from cleaned events."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.features.possession import possession_features
from src.features.spatial import spatial_features


def build_match_signatures(events: pd.DataFrame, long_pass_threshold: float = 30.0, grid_length: int = 6, grid_width: int = 5) -> pd.DataFrame:
    """Return one labelled signature vector for every team-match combination."""
    rows: list[dict[str, float | str | int]] = []
    for match_id, match_events in events.groupby("match_id"):
        for team in sorted(match_events["team"].dropna().unique()):
            row: dict[str, float | str | int] = {"match_id": match_id, "team": team}
            row.update(possession_features(match_events, team, long_pass_threshold))
            row.update(spatial_features(match_events, team, grid_length, grid_width))
            rows.append(row)
    return pd.DataFrame(rows).sort_values(["team", "match_id"]).reset_index(drop=True) if rows else pd.DataFrame()


def aggregate_season_signatures(match_signatures: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-match vectors into per-team mean and standard-deviation features."""
    if match_signatures.empty:
        return pd.DataFrame()
    feature_columns = [column for column in match_signatures.columns if column not in {"team", "match_id"}]
    means = match_signatures.groupby("team", as_index=True)[feature_columns].mean().add_suffix("_mean")
    stds = match_signatures.groupby("team", as_index=True)[feature_columns].std(ddof=0).fillna(0).add_suffix("_std")
    sample_sizes = match_signatures.groupby("team")["match_id"].nunique().rename("matches_played")
    return means.join(stds).join(sample_sizes).reset_index()


def build_signatures(events: pd.DataFrame, mode: str = "season", output_path: Path | None = None, **kwargs: float | int) -> pd.DataFrame:
    """Build per-match or season signatures and optionally persist them as Parquet."""
    if mode not in {"season", "per-match"}:
        raise ValueError("mode must be 'season' or 'per-match'")
    matches = build_match_signatures(events, **kwargs)
    result = aggregate_season_signatures(matches) if mode == "season" else matches
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_parquet(output_path, index=False)
    return result
