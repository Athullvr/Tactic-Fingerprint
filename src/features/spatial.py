"""Spatial-action distributions and territorial style features."""
from __future__ import annotations

import numpy as np
import pandas as pd


def zone_column(length_bin: int, width_bin: int) -> str:
    """Return the stable feature name for a pitch-grid cell."""
    return f"zone_l{length_bin}_w{width_bin}"


def assign_grid(x: float, y: float, grid_length: int = 6, grid_width: int = 5) -> tuple[int, int]:
    """Assign normalised 0..1 coordinates to a lengthwise/widthwise grid cell."""
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise ValueError("Coordinates must be normalised to the inclusive range 0..1.")
    return min(int(x * grid_length), grid_length - 1), min(int(y * grid_width), grid_width - 1)


def spatial_features(events: pd.DataFrame, team: str, grid_length: int = 6, grid_width: int = 5) -> dict[str, float]:
    """Compute zone action shares, defensive action height, and width dispersion."""
    action_types = {"Pass", "Carry", "Pressure", "Ball Recovery"}
    defensive_types = {"Pressure", "Ball Recovery", "Duel"}
    actions = events[(events["team"] == team) & events["event_type"].isin(action_types)].dropna(subset=["x", "y"])
    result = {zone_column(l, w): 0.0 for l in range(grid_length) for w in range(grid_width)}
    if not actions.empty:
        bins = actions.apply(lambda row: assign_grid(float(row.x), float(row.y), grid_length, grid_width), axis=1)
        for cell, count in bins.value_counts().items():
            result[zone_column(*cell)] = float(count / len(actions))
    defensive = events[(events["team"] == team) & events["event_type"].isin(defensive_types)].dropna(subset=["x"])
    result["avg_action_height"] = float(defensive["x"].mean()) if not defensive.empty else 0.0
    result["width_dispersion"] = float(actions["y"].std(ddof=0)) if not actions.empty else 0.0
    return result
