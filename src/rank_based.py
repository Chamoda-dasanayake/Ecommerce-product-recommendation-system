"""
rank_based.py
Popularity / rank-based product recommendation.
Products are ranked by average rating (weighted by number of ratings).
"""

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner="🏆 Computing popular products...")
def get_popular_products(_df_final: pd.DataFrame, min_interactions: int = 50, n: int = 10) -> pd.DataFrame:
    """
    Return the top-n most popular products.

    Parameters
    ----------
    _df_final       : filtered ratings DataFrame (user_id, prod_id, rating)
    min_interactions: minimum number of ratings a product must have
    n               : number of products to return

    Returns
    -------
    DataFrame with columns [prod_id, avg_rating, num_ratings, score]
    sorted by score descending.
    """
    grouped = (
        _df_final.groupby("prod_id")["rating"]
        .agg(avg_rating="mean", num_ratings="count")
        .reset_index()
    )

    # Keep only products with enough ratings
    popular = grouped[grouped["num_ratings"] >= min_interactions].copy()

    # Weighted score: balance between avg_rating and popularity
    max_ratings = popular["num_ratings"].max()
    popular["score"] = (
        popular["avg_rating"] * (popular["num_ratings"] / max_ratings)
    ).round(4)

    popular = popular.sort_values("score", ascending=False).head(n).reset_index(drop=True)
    popular.index += 1  # 1-based rank
    popular["avg_rating"] = popular["avg_rating"].round(2)

    return popular
