import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from config import DATA_PATH, MAX_ROWS, TOP_N
from model import enrich_product

logger = logging.getLogger(__name__)

_BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CBF_CACHE_FILE = os.path.join(_BASE_DIR, "cbf_cache.pkl")

_item_ids    = []
_cosine_sim  = None
_asin_to_idx = {}


def is_cbf_loaded() -> bool:
    return _cosine_sim is not None


def recommend_similar(asin: str, n: int = TOP_N) -> list[dict]:
    _ensure_cbf_model()

    if asin not in _asin_to_idx:
        logger.warning("CBF: ASIN '%s' not found in catalogue.", asin)
        return []

    idx    = _asin_to_idx[asin]
    scores = _cosine_sim[idx]

    sorted_indices = np.argsort(scores)[::-1]

    results = []
    rank    = 1
    for i in sorted_indices:
        if i == idx:
            continue
        if scores[i] <= 0:
            break
        results.append(enrich_product(_item_ids[i], rank))
        rank += 1
        if rank > n:
            break

    return results


def build_cbf_model():
    _build_and_cache()


def _ensure_cbf_model():
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
    global _item_ids, _cosine_sim, _asin_to_idx

    logger.info("CBF: Reading CSV: %s  (max_rows=%s)", DATA_PATH, MAX_ROWS)
    df = pd.read_csv(
        DATA_PATH,
        header=None,
        names=["user_id", "product_id", "rating", "timestamp"],
        nrows=MAX_ROWS,
        dtype={"user_id": str, "product_id": str, "rating": float},
    )
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)]

    unique_asins = df["product_id"].dropna().unique().tolist()
    logger.info("CBF: Found %d unique ASINs.", len(unique_asins))

    def _feature_string(asin: str) -> str:
        p            = enrich_product(asin, rank=1)
        category_slug = p["category"].replace(" ", "_")
        brand_slug    = p["brand"].replace(" ", "_")
        price_tier    = _price_tier(p["price"])
        rating_tier   = _rating_tier(p["rating"])
        return (
            f"{category_slug} {category_slug} "
            f"{brand_slug} "
            f"price_{price_tier} "
            f"rating_{rating_tier}"
        )

    feature_docs = [_feature_string(a) for a in unique_asins]

    logger.info("CBF: Vectorising feature documents …")
    tfidf        = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(feature_docs)
    logger.info("CBF: TF-IDF matrix shape: %s", tfidf_matrix.shape)

    logger.info("CBF: Computing cosine similarity …")
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    logger.info("CBF: Similarity matrix shape: %s", cosine_sim.shape)

    _item_ids    = unique_asins
    _cosine_sim  = cosine_sim
    _asin_to_idx = {a: i for i, a in enumerate(unique_asins)}

    logger.info("CBF: Saving cache to %s", CBF_CACHE_FILE)
    with open(CBF_CACHE_FILE, "wb") as f:
        pickle.dump({
            "item_ids":    _item_ids,
            "cosine_sim":  _cosine_sim,
            "asin_to_idx": _asin_to_idx,
        }, f)
    logger.info("CBF: Cache saved successfully.")


def _load_from_cache():
    global _item_ids, _cosine_sim, _asin_to_idx

    with open(CBF_CACHE_FILE, "rb") as f:
        cache = pickle.load(f)

    _item_ids    = cache["item_ids"]
    _cosine_sim  = cache["cosine_sim"]
    _asin_to_idx = cache["asin_to_idx"]
    logger.info("CBF: Loaded from cache (%d items).", len(_item_ids))


def _price_tier(price: float) -> int:
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
    if rating < 4.0:
        return 1
    elif rating < 4.5:
        return 2
    else:
        return 3
