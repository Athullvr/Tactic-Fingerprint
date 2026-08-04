"""Pure possession and passing feature functions."""
from __future__ import annotations

import numpy as np
import pandas as pd


def possession_features(events: pd.DataFrame, team: str, long_pass_threshold: float = 30.0) -> dict[str, float]:
    """Compute a team's possession and passing style metrics from cleaned events."""
    team_events = events[events["team"] == team]
    possession_types = {"Pass", "Carry", "Ball Receipt*"}
    total_possessions = events[events["event_type"].isin(possession_types)].shape[0]
    own_possessions = team_events[team_events["event_type"].isin(possession_types)].shape[0]
    passes = team_events[team_events["event_type"] == "Pass"].copy()
    completed = passes[passes["pass_outcome"].isna()].copy()
    lengths = np.hypot((completed["end_x"] - completed["x"]) * 120, (completed["end_y"] - completed["y"]) * 80).dropna()
    valid_passes = completed.dropna(subset=["x", "end_x"])
    first_minute = float(team_events["minute"].min()) if not team_events.empty else 0.0
    last_minute = float(team_events["minute"].max()) if not team_events.empty else 0.0
    possession_minutes = max(last_minute - first_minute, 1.0) * (own_possessions / max(total_possessions, 1))
    return {
        "possession_share": own_possessions / max(total_possessions, 1),
        "avg_pass_length": float(lengths.mean()) if not lengths.empty else 0.0,
        "long_pass_ratio": float((lengths > long_pass_threshold).mean()) if not lengths.empty else 0.0,
        "forward_pass_ratio": float((valid_passes["end_x"] > valid_passes["x"]).mean()) if not valid_passes.empty else 0.0,
        "circulation_tempo": len(completed) / possession_minutes,
    }
