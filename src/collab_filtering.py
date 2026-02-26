"""
collab_filtering.py
User-based collaborative filtering using cosine similarity.
"""

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_data(show_spinner="🔢 Building interaction matrix...")
def build_interaction_matrix(_df_final: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot df_final into a user × product matrix (NaN → 0).
    Returns the matrix and a mapping from user_id to integer index.
    """
    matrix = (
        _df_final.pivot_table(index="user_id", columns="prod_id", values="rating")
        .fillna(0)
    )
    return matrix


@st.cache_data(show_spinner="👥 Finding similar users...")
def get_similar_users(user_id: str, _interactions_matrix: pd.DataFrame, n: int = 10):
    """
    Return top-n users most similar to user_id (excluding themselves).
    Returns list of (similar_user_id, similarity_score) tuples.
    """
    if user_id not in _interactions_matrix.index:
        return []

    user_vec = _interactions_matrix.loc[[user_id]].values
    all_vecs = _interactions_matrix.values
    sims = cosine_similarity(user_vec, all_vecs).flatten()

    sim_series = pd.Series(sims, index=_interactions_matrix.index)
    sim_series = sim_series.drop(index=user_id).sort_values(ascending=False)

    return list(zip(sim_series.index[:n], sim_series.values[:n]))


def recommend_user_based(
    user_id: str,
    _df_final: pd.DataFrame,
    _interactions_matrix: pd.DataFrame,
    n: int = 5,
    num_similar: int = 10,
) -> pd.DataFrame:
    """
    Recommend top-n products for user_id based on what similar users liked.

    Strategy:
    - Find the top similar users.
    - Collect products those users rated that this user has NOT rated.
    - Rank by weighted score (similarity × rating).
    """
    similar = get_similar_users(user_id, _interactions_matrix, n=num_similar)
    if not similar:
        return pd.DataFrame(columns=["prod_id", "weighted_score", "num_similar_users"])

    # Products the target user already interacted with
    observed = set(
        _df_final[_df_final["user_id"] == user_id]["prod_id"].tolist()
    )

    scores: dict[str, list] = {}

    for sim_user, sim_score in similar:
        sim_user_data = _df_final[_df_final["user_id"] == sim_user]
        for _, row in sim_user_data.iterrows():
            pid = row["prod_id"]
            if pid not in observed:
                if pid not in scores:
                    scores[pid] = []
                scores[pid].append(sim_score * row["rating"])

    if not scores:
        return pd.DataFrame(columns=["prod_id", "weighted_score", "num_similar_users"])

    records = [
        {
            "prod_id": pid,
            "weighted_score": round(np.mean(vals), 4),
            "num_similar_users": len(vals),
        }
        for pid, vals in scores.items()
    ]

    result = (
        pd.DataFrame(records)
        .sort_values("weighted_score", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    result.index += 1
    return result
