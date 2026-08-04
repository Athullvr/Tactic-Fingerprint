from __future__ import annotations

import pytest

from src.features.possession import possession_features


def test_possession_features_are_computed(events):
    result = possession_features(events, "Alpha", long_pass_threshold=30)
    assert result["possession_share"] == pytest.approx(3 / 5)
    assert result["avg_pass_length"] > 30
    assert result["forward_pass_ratio"] == 1.0
    assert result["long_pass_ratio"] == 1.0


def test_empty_team_has_safe_zero_metrics(events):
    result = possession_features(events, "Missing")
    assert all(value == 0 for value in result.values())
