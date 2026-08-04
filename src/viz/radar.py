"""Radar chart for the readable portion of a Tactical DNA Signature."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

RADAR_FEATURES = ["possession_share", "avg_pass_length", "forward_pass_ratio", "long_pass_ratio", "avg_action_height", "width_dispersion"]


def _column(frame: pd.DataFrame, feature: str) -> str:
    return feature if feature in frame else f"{feature}_mean"


def radar_figure(signature_df: pd.DataFrame, team: str, comparison_team: str | None = None) -> go.Figure:
    """Create a league-normalised Plotly radar for one or two selected teams."""
    teams = [team] + ([comparison_team] if comparison_team else [])
    columns = [_column(signature_df, feature) for feature in RADAR_FEATURES]
    labels = [feature.replace("_", " ").title() for feature in RADAR_FEATURES]
    figure = go.Figure()
    for selected in teams:
        row = signature_df.loc[signature_df["team"] == selected]
        if row.empty:
            raise KeyError(f"Unknown team: {selected}")
        values = []
        for column in columns:
            series = signature_df[column].astype(float)
            span = series.max() - series.min()
            values.append(float((row.iloc[0][column] - series.min()) / span) if span else 0.5)
        figure.add_trace(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]], fill="toself", name=selected, opacity=0.55))
    return figure.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 1]}}, title="Tactical DNA Fingerprint", showlegend=True)
