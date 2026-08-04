"""Event-table cleaning and StatsBomb coordinate normalisation."""
from __future__ import annotations

import ast
from typing import Any

import numpy as np
import pandas as pd

PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0


def _point(value: Any) -> tuple[float, float] | None:
    """Safely coerce a StatsBomb location representation to a coordinate pair."""
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return None
    if isinstance(value, (list, tuple, np.ndarray)) and len(value) >= 2:
        try:
            return float(value[0]), float(value[1])
        except (TypeError, ValueError):
            return None
    return None


def clean_events(events: pd.DataFrame) -> pd.DataFrame:
    """Standardise an event table into a compact feature-engineering schema.

    Coordinates are scaled from StatsBomb's 120x80 pitch to 0..1. Open Data does
    not expose a universal attacking-direction field, so this function preserves
    the provider orientation; callers with known directions may flip ``x`` first.
    """
    if events.empty:
        return pd.DataFrame(columns=["match_id", "team", "event_type", "minute", "x", "y", "end_x", "end_y", "pass_outcome"])
    data = events.copy()
    type_col = "type" if "type" in data else "type_name"
    if type_col not in data or "team" not in data:
        raise ValueError("Events must include team and type/type_name columns.")
    event_type = data[type_col].map(lambda v: v.get("name") if isinstance(v, dict) else v)
    start = data.get("location", pd.Series(index=data.index, dtype=object)).map(_point)
    end_source = data.get("pass_end_location", data.get("end_location", pd.Series(index=data.index, dtype=object)))
    end = end_source.map(_point)
    output = pd.DataFrame({
        "match_id": data.get("match_id", pd.Series(0, index=data.index)).fillna(0),
        "team": data["team"].map(lambda v: v.get("name") if isinstance(v, dict) else v).astype(str).str.strip(),
        "event_type": event_type.astype(str),
        "minute": pd.to_numeric(data.get("minute", pd.Series(0, index=data.index)), errors="coerce").fillna(0),
        "x": start.map(lambda p: p[0] / PITCH_LENGTH if p else np.nan),
        "y": start.map(lambda p: p[1] / PITCH_WIDTH if p else np.nan),
        "end_x": end.map(lambda p: p[0] / PITCH_LENGTH if p else np.nan),
        "end_y": end.map(lambda p: p[1] / PITCH_WIDTH if p else np.nan),
        "pass_outcome": data.get("pass_outcome", pd.Series(index=data.index, dtype=object)).map(lambda v: v.get("name") if isinstance(v, dict) else v),
    })
    return output.dropna(subset=["team", "event_type"]).query("x >= 0 and x <= 1 and y >= 0 and y <= 1").reset_index(drop=True)
