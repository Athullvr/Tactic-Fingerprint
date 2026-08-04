"""PCA embeddings for comparing tactical signatures."""
from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def signature_matrix(signature_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return team labels and a zero-filled numeric feature matrix."""
    labels = signature_df[["team"]].copy() if "team" in signature_df else pd.DataFrame({"team": signature_df.index.astype(str)})
    numeric = signature_df.select_dtypes(include="number").fillna(0.0)
    if numeric.empty:
        raise ValueError("Signature table needs at least one numeric feature.")
    return labels, numeric


def pca_embedding(signature_df: pd.DataFrame, n_components: int = 2) -> tuple[pd.DataFrame, list[float]]:
    """Standardise signatures, project them with PCA, and return variance ratios."""
    labels, numeric = signature_matrix(signature_df)
    components = min(n_components, len(numeric), numeric.shape[1])
    if components < 1:
        raise ValueError("At least one team and one feature are required.")
    transformed = PCA(n_components=components, random_state=42).fit_transform(StandardScaler().fit_transform(numeric))
    result = labels.copy()
    for index in range(components):
        result[f"PC{index + 1}"] = transformed[:, index]
    return result, PCA(n_components=components, random_state=42).fit(StandardScaler().fit_transform(numeric)).explained_variance_ratio_.tolist()
