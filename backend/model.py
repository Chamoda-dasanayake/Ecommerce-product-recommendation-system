"""
model.py — Collaborative Filtering Recommendation Engine
Uses User-Based Cosine Similarity with numpy + pandas.
No C++ compiler required — works with Python 3.12 out of the box.
The trained similarity matrix is pickled so restarts are instant.
"""

import os
import pickle
import hashlib
import logging
import numpy as np
import pandas as pd
from config import DATA_PATH, CACHE_FILE, MAX_ROWS, TOP_N

logger = logging.getLogger(__name__)

# ─── Module-level state ─────────────────────────────────────────────────────

_user_item_matrix = None   # DataFrame: rows=users, cols=products, values=ratings
_similarity       = None   # numpy array: user × user cosine similarity
_user_ids         = []     # ordered list of user IDs (index → user_id)
_item_ids         = []     # ordered list of product IDs


# ─── Product metadata catalogue (for enrichment) ────────────────────────────

_CATEGORIES = [
    ("Headphones",        "🎧", "Audio"),
    ("Smart Speaker",     "🔊", "Audio"),
    ("Bluetooth Earbuds", "🎵", "Audio"),
    ("Smartphone",        "📱", "Mobile"),
    ("Phone Case",        "📲", "Mobile Accessories"),
    ("Screen Protector",  "📲", "Mobile Accessories"),
    ("Laptop",            "💻", "Computers"),
    ("Mechanical Keyboard","⌨️", "Computers"),
    ("Wireless Mouse",    "🖱️", "Computers"),
    ("USB-C Hub",         "🔌", "Computers"),
    ("Smart Watch",       "⌚", "Wearables"),
    ("Fitness Tracker",   "💪", "Wearables"),
    ("Gaming Controller", "🎮", "Gaming"),
    ("Gaming Headset",    "🎮", "Gaming"),
    ("DSLR Camera",       "📷", "Cameras"),
    ("Action Camera",     "📷", "Cameras"),
    ("Portable Charger",  "🔋", "Accessories"),
    ("Cable Set",         "🔌", "Accessories"),
    ("Smart TV",          "📺", "Home Entertainment"),
    ("Streaming Stick",   "📺", "Home Entertainment"),
    ("Tablet",            "📱", "Tablets"),
    ("E-Reader",          "📚", "Tablets"),
    ("Wireless Router",   "📡", "Networking"),
    ("Smart Home Hub",    "🏠", "Smart Home"),
]

_BRANDS = [
    "Sony", "Samsung", "Apple", "Bose", "Logitech", "JBL", "Anker",
    "LG", "Dell", "HP", "Asus", "Lenovo", "Razer", "Corsair", "Canon",
    "Nikon", "Belkin", "Philips", "Panasonic", "Xiaomi",
]

_ADJECTIVES = [
    "Pro", "Elite", "Ultra", "Max", "Plus", "Air", "Slim",
    "Edge", "Nova", "Apex", "Pulse", "Zeta", "Prime", "Flex",
]

_PRICE_RANGES = [
    (15,  50),
    (50,  150),
    (150, 400),
    (400, 800),
    (800, 1500),
]


def _asin_seed(asin: str) -> int:
    """Convert ASIN to a stable integer seed via MD5."""
    return int(hashlib.md5(asin.encode()).hexdigest(), 16)


def enrich_product(asin: str, rank: int) -> dict:
    """
    Turn an ASIN into a rich product dict.
    Uses the ASIN hash so the same ASIN always gets the same details.
    """
    seed = _asin_seed(asin)

    cat_idx   = seed % len(_CATEGORIES)
    brand_idx = (seed >> 4) % len(_BRANDS)
    adj_idx   = (seed >> 8) % len(_ADJECTIVES)
    pr_idx    = (seed >> 12) % len(_PRICE_RANGES)

    name_part, emoji, category = _CATEGORIES[cat_idx]
    brand     = _BRANDS[brand_idx]
    adj       = _ADJECTIVES[adj_idx]
    lo, hi    = _PRICE_RANGES[pr_idx]

    # Stable price within the range
    price = lo + (seed % (hi - lo + 1))

    # Stable rating between 3.5 and 5.0
    rating_raw = 3.5 + ((seed >> 16) % 16) * 0.1
    rating = round(min(5.0, rating_raw), 1)

    # Match score decreases with rank, with small ASIN-seeded jitter
    base_score = max(55, 98 - rank * 5)
    jitter = (seed >> 20) % 8
    match_score = min(99, base_score + jitter)

    return {
        "asin":       asin,
        "rank":       rank,
        "name":       f"{brand} {adj} {name_part}",
        "brand":      brand,
        "category":   category,
        "emoji":      emoji,
        "price":      price,
        "rating":     rating,
        "match_score": match_score,
    }


# ─── Public helpers ──────────────────────────────────────────────────────────

def is_model_loaded() -> bool:
    """Return True once the similarity matrix has been built / loaded."""
    return _similarity is not None


def get_sample_users(n: int = 50) -> list:
    """Return up to *n* real user IDs from the dataset."""
    _ensure_model()
    return _user_ids[:n]


def recommend_products(user_id: str, n: int = TOP_N) -> list[dict]:
    """
    Return the top-*n* enriched product dicts for *user_id* using user-based CF.
    Returns an empty list if *user_id* is not in the training set.
    """
    _ensure_model()

    if user_id not in _user_item_matrix.index:
        return []

    # Row index of target user in the matrix
    u_idx = _user_ids.index(user_id)

    # Weighted sum: for each similar user, weight their ratings by similarity score
    sim_row    = _similarity[u_idx]
    user_rated = _user_item_matrix.loc[user_id]

    # Products the target user has NOT yet rated
    unrated_mask = (user_rated == 0).values

    # Predicted score for each unrated product
    matrix_values = _user_item_matrix.values
    scores = np.dot(sim_row, matrix_values)

    # Zero out already-rated items
    scores[~unrated_mask] = 0.0

    # Pick top-n item indices
    top_indices = np.argsort(scores)[::-1][:n]
    raw_asins = [_item_ids[i] for i in top_indices if scores[i] > 0]

    # Enrich each ASIN with product metadata
    return [enrich_product(asin, rank + 1) for rank, asin in enumerate(raw_asins)]


# ─── Internal: building / loading model ────────────────────────────────────

def _ensure_model():
    """Load from cache or build if necessary (lazy, thread-safe enough for dev)."""
    global _user_item_matrix, _similarity, _user_ids, _item_ids

    if _similarity is not None:
        return

    if os.path.exists(CACHE_FILE):
        logger.info("Loading model from cache: %s", CACHE_FILE)
        _load_from_cache()
    else:
        logger.info("No cache found — building model from scratch …")
        _build_and_cache()


def _build_and_cache():
    """Build the user-item matrix and cosine similarity, then pickle."""
    global _user_item_matrix, _similarity, _user_ids, _item_ids

    # ── 1. Load data ──────────────────────────────────────────────────────────
    logger.info("Reading CSV: %s  (max_rows=%s)", DATA_PATH, MAX_ROWS)
    df = pd.read_csv(
        DATA_PATH,
        header=None,
        names=["user_id", "product_id", "rating", "timestamp"],
        nrows=MAX_ROWS,
        dtype={"user_id": str, "product_id": str, "rating": float},
    )
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)].copy()
    logger.info("Loaded %d rows after filtering.", len(df))

    # Keep only users with ≥ 5 ratings and products with ≥ 10 ratings
    user_counts    = df["user_id"].value_counts()
    product_counts = df["product_id"].value_counts()
    df = df[
        df["user_id"].isin(user_counts[user_counts >= 5].index) &
        df["product_id"].isin(product_counts[product_counts >= 10].index)
    ]
    logger.info("After frequency filter: %d rows, %d users, %d products.",
                len(df), df["user_id"].nunique(), df["product_id"].nunique())

    # ── 2. Build user-item matrix ─────────────────────────────────────────────
    matrix = df.pivot_table(
        index="user_id", columns="product_id", values="rating", fill_value=0
    )
    _user_item_matrix = matrix
    _user_ids         = list(matrix.index)
    _item_ids         = list(matrix.columns)
    logger.info("Matrix shape: %s", matrix.shape)

    # ── 3. Cosine similarity between users ────────────────────────────────────
    logger.info("Computing cosine similarity …")
    M = matrix.values.astype(np.float32)
    norms = np.linalg.norm(M, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    M_norm = M / norms
    _similarity = np.dot(M_norm, M_norm.T)
    logger.info("Similarity matrix computed: %s", _similarity.shape)

    # ── 4. Persist ────────────────────────────────────────────────────────────
    logger.info("Saving model cache to %s", CACHE_FILE)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump({
            "user_item_matrix": _user_item_matrix,
            "similarity":       _similarity,
            "user_ids":         _user_ids,
            "item_ids":         _item_ids,
        }, f)
    logger.info("Cache saved successfully.")


def _load_from_cache():
    """Restore from pickle."""
    global _user_item_matrix, _similarity, _user_ids, _item_ids

    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)

    _user_item_matrix = cache["user_item_matrix"]
    _similarity       = cache["similarity"]
    _user_ids         = cache["user_ids"]
    _item_ids         = cache["item_ids"]
    logger.info("Model loaded from cache (%d users, %d items).",
                len(_user_ids), len(_item_ids))
