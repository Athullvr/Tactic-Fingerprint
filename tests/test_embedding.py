from __future__ import annotations

import pandas as pd

from src.analysis.embedding import pca_embedding
from src.analysis.similarity import most_similar_teams


def _signatures() -> pd.DataFrame:
    return pd.DataFrame({"team": ["Alpha", "Beta", "Gamma", "Delta"], "possession_share_mean": [.6, .58, .2, .25], "long_pass_ratio_mean": [.1, .12, .8, .7], "avg_action_height_mean": [.7, .68, .3, .35]})


def test_pca_shape_and_explained_variance():
    embedding, variance = pca_embedding(_signatures(), n_components=2)
    assert embedding.shape == (4, 3)
    assert len(variance) == 2
    assert sum(variance) <= 1.0


def test_similarity_excludes_subject_team():
    result = most_similar_teams("Alpha", _signatures(), top_n=3)
    assert "Alpha" not in result.team.tolist()
    assert result.iloc[0].team == "Beta"
