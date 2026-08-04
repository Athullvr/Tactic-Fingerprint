"""Style clustering and interpretable rule-based cluster descriptions."""
from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.analysis.embedding import signature_matrix


def recommend_k(signature_df: pd.DataFrame, k_min: int = 2, k_max: int = 8) -> pd.DataFrame:
    """Evaluate valid k values and return their silhouette scores."""
    _, numeric = signature_matrix(signature_df)
    matrix = StandardScaler().fit_transform(numeric)
    rows = []
    for k in range(k_min, min(k_max, len(matrix) - 1) + 1):
        labels = KMeans(n_clusters=k, random_state=42, n_init=20).fit_predict(matrix)
        rows.append({"k": k, "silhouette_score": silhouette_score(matrix, labels)})
    return pd.DataFrame(rows)


def _feature_value(centroid: pd.Series, name: str) -> float:
    return float(centroid.get(name, centroid.get(f"{name}_mean", 0.0)))


def label_cluster(centroid: pd.Series) -> str:
    """Produce a conservative style label from standardised centroid extremes."""
    long = _feature_value(centroid, "long_pass_ratio")
    possession = _feature_value(centroid, "possession_share")
    height = _feature_value(centroid, "avg_action_height")
    width = _feature_value(centroid, "width_dispersion")
    if long > 0.35 and possession < -0.15:
        return "Direct / Counter-Attacking"
    if possession > 0.3 and long < -0.1:
        return "Possession-Controlled"
    if height > 0.3:
        return "High-Pressing"
    if width > 0.3:
        return "Wide Territorial"
    return "Balanced"


def cluster_teams(signature_df: pd.DataFrame, n_clusters: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cluster teams and return membership plus labelled standardised centroids."""
    labels, numeric = signature_matrix(signature_df)
    matrix = StandardScaler().fit_transform(numeric)
    if n_clusters is None:
        sweep = recommend_k(signature_df)
        n_clusters = int(sweep.sort_values("silhouette_score", ascending=False).iloc[0]["k"]) if not sweep.empty else 1
    n_clusters = max(1, min(n_clusters, len(matrix)))
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20).fit(matrix)
    centroids = pd.DataFrame(model.cluster_centers_, columns=numeric.columns)
    centroids.insert(0, "cluster", range(n_clusters))
    centroids["style_label"] = centroids.drop(columns="cluster").apply(label_cluster, axis=1)
    members = labels.copy()
    members["cluster"] = model.labels_
    members = members.merge(centroids[["cluster", "style_label"]], on="cluster", how="left")
    return members, centroids
