"""
model_based.py
Model-based collaborative filtering using Truncated SVD (matrix factorisation).
"""

import pandas as pd
import numpy as np
import streamlit as st
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.metrics import mean_squared_error


@st.cache_data(show_spinner="🤖 Running SVD model (may take ~20s)...")
def build_svd_model(_interactions_matrix: pd.DataFrame, k: int = 50):
    """
    Decompose the interaction matrix with SVD (k latent factors).
    Returns (preds_df) — a DataFrame of predicted ratings with same shape as interactions_matrix.
    """
    sparse_matrix = csr_matrix(_interactions_matrix.values)
    # svds returns U, sigma, Vt
    U, sigma, Vt = svds(sparse_matrix, k=k)
    sigma = np.diag(sigma)

    # Reconstruct predicted ratings
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)

    preds_df = pd.DataFrame(
        all_user_predicted_ratings,
        index=_interactions_matrix.index,
        columns=_interactions_matrix.columns,
    )
    return preds_df


def recommend_model_based(
    user_id: str,
    _interactions_matrix: pd.DataFrame,
    _preds_df: pd.DataFrame,
    n: int = 5,
) -> pd.DataFrame:
    """
    Recommend top-n products for user_id using SVD predicted ratings.
    Only recommends products the user has NOT already rated.
    """
    if user_id not in _interactions_matrix.index:
        return pd.DataFrame(columns=["prod_id", "predicted_rating"])

    user_actual = _interactions_matrix.loc[user_id]
    user_preds = _preds_df.loc[user_id]

    # Products the user hasn't rated yet (actual rating == 0)
    unrated_mask = user_actual == 0

    recs = (
        user_preds[unrated_mask]
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    recs.columns = ["prod_id", "predicted_rating"]
    recs["predicted_rating"] = recs["predicted_rating"].round(4)
    recs.index += 1
    return recs


def compute_rmse(_interactions_matrix: pd.DataFrame, _preds_df: pd.DataFrame) -> float:
    """
    Compute RMSE between actual and predicted ratings
    (only for non-zero actual ratings).
    """
    actual = _interactions_matrix.values.flatten()
    predicted = _preds_df.values.flatten()

    # Only compare where actual rating exists
    mask = actual != 0
    if mask.sum() == 0:
        return float("nan")

    rmse = np.sqrt(mean_squared_error(actual[mask], predicted[mask]))
    return round(rmse, 4)
