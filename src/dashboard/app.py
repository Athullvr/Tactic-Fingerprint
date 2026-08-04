"""Interactive Streamlit explorer for team tactical identities."""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analysis.clustering import cluster_teams
from src.analysis.embedding import pca_embedding
from src.analysis.similarity import most_similar_teams
from src.viz.pitch_heatmap import pitch_heatmap
from src.viz.radar import radar_figure

SIGNATURES = Path(__file__).resolve().parents[2] / "data/processed/team_signatures.parquet"


@st.cache_data
def load_signatures() -> pd.DataFrame:
    """Load derived signatures only; raw StatsBomb events are never read here."""
    return pd.read_parquet(SIGNATURES)


def main() -> None:
    st.set_page_config(page_title="Tactic Fingerprint", layout="wide")
    st.title("Tactic Fingerprint Generator")
    if not SIGNATURES.exists():
        st.info("No derived signatures yet. Run scripts/run_pipeline.py after downloading StatsBomb Open Data.")
        return
    signatures = load_signatures()
    teams = sorted(signatures.team.astype(str).unique())
    team = st.selectbox("Team", teams)
    comparison = st.selectbox("Compare with", ["None"] + [name for name in teams if name != team])
    st.plotly_chart(radar_figure(signatures, team, None if comparison == "None" else comparison), use_container_width=True)
    columns = st.columns(2)
    with columns[0]:
        st.subheader("Territorial action map")
        st.pyplot(pitch_heatmap(signatures.loc[signatures.team == team].iloc[0]))
    with columns[1]:
        st.subheader("Most similar teams")
        st.dataframe(most_similar_teams(team, signatures), use_container_width=True)
    members, centroids = cluster_teams(signatures)
    embedding, variance = pca_embedding(signatures)
    embedding = embedding.merge(members, on="team")
    st.subheader(f"PCA tactical map ({sum(variance):.0%} variance captured)")
    st.plotly_chart(px.scatter(embedding, x="PC1", y="PC2", color="style_label", hover_name="team"), use_container_width=True)
    cluster = st.selectbox("Cluster explorer", sorted(members.cluster.unique()))
    st.dataframe(members[members.cluster == cluster], use_container_width=True)
    st.caption(f"Style drivers: {centroids.loc[centroids.cluster == cluster, 'style_label'].iloc[0]}")


if __name__ == "__main__":
    main()
