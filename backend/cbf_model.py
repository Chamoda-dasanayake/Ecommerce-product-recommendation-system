"""
cbf_model.py — Content-Based Filtering Recommendation Engine

Builds an item-feature matrix from the product metadata produced by
enrich_product() in model.py (category, brand, price tier, rating tier).
Uses scikit-learn TfidfVectorizer + cosine similarity to find products
similar to a given ASIN.

Usage:
    from cbf_model import recommend_similar, build_cbf_model
    build_cbf_model()          # call once at startup (or use lazy load)
    recs = recommend_similar("B00004NKIQ", n=10)
"""

import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from config import DATA_PATH, MAX_ROWS, TOP_N
from model import enrich_product  # reuse the same metadata logic

logger = logging.getLogger(__name__)

# ── Cache path for CBF model ───────────────────────────────────────────────
_BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CBF_CACHE_FILE = os.path.join(_BASE_DIR, "cbf_cache.pkl")

# ── Module-level state ─────────────────────────────────────────────────────
_item_ids     = []    # list of ASIN strings (row index ↔ ASIN)
_cosine_sim   = None  # numpy ndarray: item × item cosine similarity
_asin_to_idx  = {}    # dict: asin → row index for O(1) lookup


# ─── Public API ──────────────────────────────────────────────────────────────

def is_cbf_loaded() -> bool:
    """Return True when the CBF model is ready to serve requests."""
    return _cosine_sim is not None


def recommend_similar(asin: str, n: int = TOP_N) -> list[dict]:
    """
    Return the top-n enriched product dicts most similar to *asin*.

    Parameters
    ----------
    asin : str
        The reference product ASIN.
    n : int
        Number of recommendations to return.

    Returns
    -------
    list[dict]
        Enriched product dicts (same shape as collaborative-filtering output),
        or an empty list if *asin* is not in the catalogue.
    """
    _ensure_cbf_model()

    if asin not in _asin_to_idx:
        logger.warning("CBF: ASIN '%s' not found in catalogue.", asin)
        return []

    idx    = _asin_to_idx[asin]
    scores = _cosine_sim[idx]  # similarity to every other item

    # Sort descending; skip index 0 (the query item itself)
    sorted_indices = np.argsort(scores)[::-1]

    results = []
    rank = 1
    for i in sorted_indices:
        if i == idx:
            continue  # skip the query product
        if scores[i] <= 0:
            break
        results.append(enrich_product(_item_ids[i], rank))
        rank += 1
        if rank > n:
            break

    return results


def build_cbf_model():
    """
    Public entry-point to explicitly trigger a (re)build of the CBF model.
    Normally you do not need to call this — _ensure_cbf_model() is lazy.
    """
    _build_and_cache()


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _ensure_cbf_model():
    """Lazy-load: build from scratch or restore from cache."""
    global _cosine_sim
    if _cosine_sim is not None:
        return
    if os.path.exists(CBF_CACHE_FILE):
        logger.info("CBF: Loading from cache: %s", CBF_CACHE_FILE)
        _load_from_cache()
    else:
        logger.info("CBF: No cache found — building from scratch …")
        _build_and_cache()


def _build_and_cache():
    """Build the item-feature matrix + cosine similarity, then pickle."""
    global _item_ids, _cosine_sim, _asin_to_idx

    # ── 1. Load ASIN catalogue from the ratings CSV ───────────────────────
    logger.info("CBF: Reading CSV: %s  (max_rows=%s)", DATA_PATH, MAX_ROWS)
    df = pd.read_csv(
        DATA_PATH,
        header=None,
        names=["user_id", "product_id", "rating", "timestamp"],
        nrows=MAX_ROWS,
        dtype={"user_id": str, "product_id": str, "rating": float},
    )
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)]

    # One row per unique ASIN (we only care about product IDs here)
    unique_asins = df["product_id"].dropna().unique().tolist()
    logger.info("CBF: Found %d unique ASINs.", len(unique_asins))

    # ── 2. Build feature strings for each ASIN ────────────────────────────
    # Each ASIN gets a "document" like:
    #   "Audio Audio Bose Elite Headphones tier_2 rating_4"
    # TF-IDF converts this into a sparse vector.

    def _feature_string(asin: str) -> str:
        p = enrich_product(asin, rank=1)
        # Repeat category twice to give it slightly more weight
        category_slug = p["category"].replace(" ", "_")
        brand_slug    = p["brand"].replace(" ", "_")
        # Bucket price into 5 tiers
        price_tier = _price_tier(p["price"])
        # Bucket rating into 3 tiers
        rating_tier = _rating_tier(p["rating"])
        return (
            f"{category_slug} {category_slug} "
            f"{brand_slug} "
            f"price_{price_tier} "
            f"rating_{rating_tier}"
        )

    feature_docs = [_feature_string(a) for a in unique_asins]

    # ── 3. TF-IDF vectorisation ───────────────────────────────────────────
    logger.info("CBF: Vectorising feature documents …")
    tfidf  = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(feature_docs)
    logger.info("CBF: TF-IDF matrix shape: %s", tfidf_matrix.shape)

    # ── 4. Item-item cosine similarity ────────────────────────────────────
    logger.info("CBF: Computing cosine similarity (this may take a moment) …")
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    logger.info("CBF: Similarity matrix shape: %s", cosine_sim.shape)

    # ── 5. Store in module state ──────────────────────────────────────────
    _item_ids    = unique_asins
    _cosine_sim  = cosine_sim
    _asin_to_idx = {a: i for i, a in enumerate(unique_asins)}

    # ── 6. Persist ────────────────────────────────────────────────────────
    logger.info("CBF: Saving cache to %s", CBF_CACHE_FILE)
    with open(CBF_CACHE_FILE, "wb") as f:
        pickle.dump({
            "item_ids":    _item_ids,
            "cosine_sim":  _cosine_sim,
            "asin_to_idx": _asin_to_idx,
        }, f)
    logger.info("CBF: Cache saved successfully.")


def _load_from_cache():
    """Restore CBF model from pickle."""
    global _item_ids, _cosine_sim, _asin_to_idx

    with open(CBF_CACHE_FILE, "rb") as f:
        cache = pickle.load(f)

    _item_ids    = cache["item_ids"]
    _cosine_sim  = cache["cosine_sim"]
    _asin_to_idx = cache["asin_to_idx"]
    logger.info("CBF: Loaded from cache (%d items).", len(_item_ids))


# ─── Feature bucketing helpers ───────────────────────────────────────────────

def _price_tier(price: float) -> int:
    """Map a price to one of 5 tiers (1 = cheapest)."""
    if price < 50:
        return 1
    elif price < 150:
        return 2
    elif price < 400:
        return 3
    elif price < 800:
        return 4
    else:
        return 5


def _rating_tier(rating: float) -> int:
    """Map a rating (0-5) to one of 3 tiers."""
    if rating < 4.0:
        return 1
    elif rating < 4.5:
        return 2
    else:
        return 3
