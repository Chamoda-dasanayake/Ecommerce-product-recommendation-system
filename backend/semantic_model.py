import os
import pickle
import logging
import numpy as np
import pandas as pd

from config import DATA_PATH, MAX_ROWS, TOP_N
from model import enrich_product

logger = logging.getLogger(__name__)

_BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
SEMANTIC_CACHE_FILE = os.path.join(_BASE_DIR, "semantic_cache.pkl")

_product_asins   = []
_product_vectors = None   # ndarray (n_products, embedding_dim), L2-normalised
_st_model        = None   # SentenceTransformer instance


def is_semantic_loaded() -> bool:
    return _product_vectors is not None


def semantic_search(query: str, n: int = TOP_N) -> list[dict]:
    """
    Encode the free-text query and return the top-n products by cosine similarity.
    Products are built from the ASIN catalogue using enrich_product() metadata.
    """
    _ensure_semantic_model()

    query_vec = _st_model.encode([query], normalize_embeddings=True)     # (1, dim)
    scores    = np.dot(_product_vectors, query_vec.T).squeeze()           # (n_products,)

    top_indices = np.argsort(scores)[::-1][:n]

    results = []
    for rank, idx in enumerate(top_indices):
        if float(scores[idx]) <= 0:
            break
        product               = enrich_product(_product_asins[idx], rank + 1)
        product["match_score"] = min(99, round(float(scores[idx]) * 100))
        results.append(product)

    return results


def _ensure_semantic_model():
    global _product_vectors, _product_asins, _st_model

    if _product_vectors is not None:
        return

    logger.info("Semantic: Loading SentenceTransformer (all-MiniLM-L6-v2)…")
    from sentence_transformers import SentenceTransformer
    _st_model = SentenceTransformer("all-MiniLM-L6-v2")

    if os.path.exists(SEMANTIC_CACHE_FILE):
        logger.info("Semantic: Loading vector cache: %s", SEMANTIC_CACHE_FILE)
        _load_from_cache()
    else:
        logger.info("Semantic: Building embeddings from scratch…")
        _build_and_cache()


def _build_and_cache():
    global _product_asins, _product_vectors

    logger.info("Semantic: Reading CSV: %s", DATA_PATH)
    df = pd.read_csv(
        DATA_PATH,
        header=None,
        names=["user_id", "product_id", "rating", "timestamp"],
        nrows=MAX_ROWS,
        dtype={"user_id": str, "product_id": str, "rating": float},
    )
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)]
    unique_asins = df["product_id"].dropna().unique().tolist()
    logger.info("Semantic: Found %d unique ASINs.", len(unique_asins))

    texts = []
    for asin in unique_asins:
        p = enrich_product(asin, rank=1)
        texts.append(
            f"{p['name']} {p['product_type']} {p['category']} {p['brand']}"
        )

    logger.info("Semantic: Encoding %d product descriptions…", len(texts))
    vectors = _st_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    logger.info("Semantic: Embeddings shape: %s", vectors.shape)

    _product_asins   = unique_asins
    _product_vectors = vectors.astype(np.float32)

    logger.info("Semantic: Saving cache to %s", SEMANTIC_CACHE_FILE)
    with open(SEMANTIC_CACHE_FILE, "wb") as f:
        pickle.dump({"asins": _product_asins, "vectors": _product_vectors}, f)
    logger.info("Semantic: Cache saved successfully.")


def _load_from_cache():
    global _product_asins, _product_vectors

    with open(SEMANTIC_CACHE_FILE, "rb") as f:
        data = pickle.load(f)

    _product_asins   = data["asins"]
    _product_vectors = data["vectors"]
    logger.info("Semantic: Loaded %d product vectors from cache.", len(_product_asins))
