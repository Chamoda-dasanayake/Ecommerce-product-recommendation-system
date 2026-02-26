"""
data_loader.py
Handles loading and preprocessing the Amazon Electronics ratings dataset.
"""

import pandas as pd
import numpy as np
import streamlit as st
import os


DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ratings_Electronics.csv")


@st.cache_data(show_spinner="📦 Loading dataset... (this takes ~30s the first time)")
def load_and_preprocess(min_ratings: int = 50):
    """
    Load raw CSV, clean it, and return:
      - df       : full raw dataframe (user_id, prod_id, rating)
      - df_final : filtered to users with >= min_ratings
    """
    if not os.path.exists(DATA_PATH):
        return None, None

    df = pd.read_csv(DATA_PATH, header=None)
    df.columns = ["user_id", "prod_id", "rating", "timestamp"]
    df = df.drop("timestamp", axis=1)

    # Filter to active users only
    counts = df["user_id"].value_counts()
    df_final = df[df["user_id"].isin(counts[counts >= min_ratings].index)].copy()

    return df, df_final


def get_stats(df, df_final):
    """Return a dict of key dataset statistics."""
    if df is None or df_final is None:
        return {}
    return {
        "total_ratings": len(df),
        "total_users": df["user_id"].nunique(),
        "total_products": df["prod_id"].nunique(),
        "filtered_ratings": len(df_final),
        "filtered_users": df_final["user_id"].nunique(),
        "filtered_products": df_final["prod_id"].nunique(),
        "avg_rating": round(df["rating"].mean(), 2),
        "rating_counts": df["rating"].value_counts().sort_index(),
        "top_users": df.groupby("user_id").size().sort_values(ascending=False).head(10),
    }


def get_user_list(df_final):
    """Return sorted list of unique user IDs in filtered data."""
    return sorted(df_final["user_id"].unique().tolist())
