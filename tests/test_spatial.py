from __future__ import annotations

import pytest

from src.features.spatial import assign_grid, spatial_features, zone_column


def test_grid_assignment_handles_pitch_boundaries():
    assert assign_grid(0.0, 0.0) == (0, 0)
    assert assign_grid(0.99, 0.99) == (5, 4)
    assert assign_grid(1.0, 1.0) == (5, 4)
    with pytest.raises(ValueError):
        assign_grid(1.01, .5)


def test_spatial_distribution_sums_to_one(events):
    result = spatial_features(events, "Alpha")
    zones = [value for key, value in result.items() if key.startswith("zone_")]
    assert sum(zones) == pytest.approx(1.0)
    assert result[zone_column(0, 1)] > 0
    assert result["avg_action_height"] == pytest.approx(.75)
