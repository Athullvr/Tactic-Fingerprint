"""Team similarity rankings on standardised tactical signatures."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from src.analysis.embedding import signature_matrix


def most_similar_teams(team_name: str, signature_df: pd.DataFrame, top_n: int = 5, metric: str = "cosine") -> pd.DataFrame:
    """Rank every other team by cosine similarity or Euclidean distance."""
    labels, numeric = signature_matrix(signature_df)
    names = labels["team"].astype(str).tolist()
    if team_name not in names:
        raise KeyError(f"Unknown team: {team_name}")
    matrix = StandardScaler().fit_transform(numeric)
    index = names.index(team_name)
    if metric == "cosine":
        values = cosine_similarity(matrix[index : index + 1], matrix).ravel()
        result = pd.DataFrame({"team": names, "similarity": values}).drop(index=index).sort_values("similarity", ascending=False)
    elif metric == "euclidean":
        values = np.linalg.norm(matrix - matrix[index], axis=1)
        result = pd.DataFrame({"team": names, "distance": values}).drop(index=index).sort_values("distance")
    else:
        raise ValueError("metric must be 'cosine' or 'euclidean'")
    return result.head(top_n).reset_index(drop=True)
