"""Pitch-grid action heatmap rendering."""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from mplsoccer import Pitch

from src.features.spatial import zone_column


def pitch_heatmap(signature_row: pd.Series, grid_length: int = 6, grid_width: int = 5) -> Figure:
    """Draw a 30-zone action-share heatmap for one signature row."""
    values = np.array([[signature_row.get(zone_column(l, w), signature_row.get(f"{zone_column(l, w)}_mean", 0.0)) for l in range(grid_length)] for w in range(grid_width)])
    pitch = Pitch(pitch_type="statsbomb", line_color="#202020")
    figure, axis = pitch.draw(figsize=(12, 8))
    image = axis.imshow(values, extent=(0, 120, 80, 0), alpha=0.75, cmap="magma", aspect="auto")
    figure.colorbar(image, ax=axis, label="Action share")
    return figure
