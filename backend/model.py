import os
import pickle
import hashlib
import logging
import numpy as np
import pandas as pd
from config import DATA_PATH, CACHE_FILE, MAX_ROWS, TOP_N

logger = logging.getLogger(__name__)

_user_item_matrix = None
_similarity       = None
_user_ids         = []
_item_ids         = []

_CATEGORIES = [
    ("Headphones",         "🎧", "Audio"),
    ("Smart Speaker",      "🔊", "Audio"),
    ("Bluetooth Earbuds",  "🎵", "Audio"),
    ("Smartphone",         "📱", "Mobile"),
    ("Phone Case",         "📲", "Mobile Accessories"),
    ("Screen Protector",   "📲", "Mobile Accessories"),
    ("Laptop",             "💻", "Computers"),
    ("Mechanical Keyboard","⌨️", "Computers"),
    ("Wireless Mouse",     "🖱️", "Computers"),
    ("USB-C Hub",          "🔌", "Computers"),
    ("Smart Watch",        "⌚", "Wearables"),
    ("Fitness Tracker",    "💪", "Wearables"),
    ("Gaming Controller",  "🎮", "Gaming"),
    ("Gaming Headset",     "🎮", "Gaming"),
    ("DSLR Camera",        "📷", "Cameras"),
    ("Action Camera",      "📷", "Cameras"),
    ("Portable Charger",   "🔋", "Accessories"),
    ("Cable Set",          "🔌", "Accessories"),
    ("Smart TV",           "📺", "Home Entertainment"),
    ("Streaming Stick",    "📺", "Home Entertainment"),
    ("Tablet",             "📱", "Tablets"),
    ("E-Reader",           "📚", "Tablets"),
    ("Wireless Router",    "📡", "Networking"),
    ("Smart Home Hub",     "🏠", "Smart Home"),
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
    return int(hashlib.md5(asin.encode()).hexdigest(), 16)


def enrich_product(asin: str, rank: int) -> dict:
    seed = _asin_seed(asin)

    cat_idx   = seed % len(_CATEGORIES)
    brand_idx = (seed >> 4) % len(_BRANDS)
    adj_idx   = (seed >> 8) % len(_ADJECTIVES)
    pr_idx    = (seed >> 12) % len(_PRICE_RANGES)

    name_part, emoji, category = _CATEGORIES[cat_idx]
    brand  = _BRANDS[brand_idx]
    adj    = _ADJECTIVES[adj_idx]
    lo, hi = _PRICE_RANGES[pr_idx]

    price      = lo + (seed % (hi - lo + 1))
    rating_raw = 3.5 + ((seed >> 16) % 16) * 0.1
    rating     = round(min(5.0, rating_raw), 1)

    base_score  = max(55, 98 - rank * 5)
    jitter      = (seed >> 20) % 8
    match_score = min(99, base_score + jitter)

    return {
        "asin":         asin,
        "rank":         rank,
        "name":         f"{brand} {adj} {name_part}",
        "product_type": name_part,
        "brand":        brand,
        "category":     category,
        "emoji":        emoji,
        "price":        price,
        "rating":       rating,
        "match_score":  match_score,
    }


def is_model_loaded() -> bool:
    return _similarity is not None


def get_sample_users(n: int = 50) -> list:
    _ensure_model()
    return _user_ids[:n]


def recommend_products(user_id: str, n: int = TOP_N) -> list[dict]:
    _ensure_model()

    if user_id not in _user_item_matrix.index:
        return []

    u_idx      = _user_ids.index(user_id)
    sim_row    = _similarity[u_idx]
    user_rated = _user_item_matrix.loc[user_id]

    unrated_mask  = (user_rated == 0).values
    matrix_values = _user_item_matrix.values
    scores        = np.dot(sim_row, matrix_values)
    scores[~unrated_mask] = 0.0

    top_indices = np.argsort(scores)[::-1][:n]
    raw_asins   = [_item_ids[i] for i in top_indices if scores[i] > 0]

    return [enrich_product(asin, rank + 1) for rank, asin in enumerate(raw_asins)]


def get_cf_scores(user_id: str) -> dict:
    """
    Return a min-max normalised {asin: score} dict for all items the user
    has NOT yet rated.  Used by the hybrid model to fuse with CBF scores.
    Returns an empty dict if user_id is not in the training set.
    """
    _ensure_model()

    if user_id not in _user_item_matrix.index:
        return {}

    u_idx      = _user_ids.index(user_id)
    sim_row    = _similarity[u_idx]
    user_rated = _user_item_matrix.loc[user_id]

    unrated_mask  = (user_rated == 0).values
    scores        = np.dot(sim_row, _user_item_matrix.values)
    scores[~unrated_mask] = 0.0

    s_min, s_max = scores.min(), scores.max()
    if s_max - s_min < 1e-9:
        return {}

    normed = (scores - s_min) / (s_max - s_min)
    return {_item_ids[i]: float(normed[i]) for i in range(len(_item_ids)) if normed[i] > 0}


def _ensure_model():
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
    global _user_item_matrix, _similarity, _user_ids, _item_ids

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

    user_counts    = df["user_id"].value_counts()
    product_counts = df["product_id"].value_counts()
    df = df[
        df["user_id"].isin(user_counts[user_counts >= 5].index) &
        df["product_id"].isin(product_counts[product_counts >= 10].index)
    ]
    logger.info("After frequency filter: %d rows, %d users, %d products.",
                len(df), df["user_id"].nunique(), df["product_id"].nunique())

    matrix            = df.pivot_table(index="user_id", columns="product_id", values="rating", fill_value=0)
    _user_item_matrix = matrix
    _user_ids         = list(matrix.index)
    _item_ids         = list(matrix.columns)
    logger.info("Matrix shape: %s", matrix.shape)

    logger.info("Computing cosine similarity …")
    M = matrix.values.astype(np.float32)
    norms = np.linalg.norm(M, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    M_norm      = M / norms
    _similarity = np.dot(M_norm, M_norm.T)
    logger.info("Similarity matrix computed: %s", _similarity.shape)

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
    global _user_item_matrix, _similarity, _user_ids, _item_ids

    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)

    _user_item_matrix = cache["user_item_matrix"]
    _similarity       = cache["similarity"]
    _user_ids         = cache["user_ids"]
    _item_ids         = cache["item_ids"]
    logger.info("Model loaded from cache (%d users, %d items).", len(_user_ids), len(_item_ids))
