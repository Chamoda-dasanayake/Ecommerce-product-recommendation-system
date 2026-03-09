import logging
from config import TOP_N
from model import get_cf_scores, enrich_product
from cbf_model import get_cbf_scores

logger = logging.getLogger(__name__)

CF_WEIGHT  = 0.6
CBF_WEIGHT = 0.4


def hybrid_recommend(user_id: str, n: int = TOP_N) -> list[dict]:
    """
    Hybrid recommendation: Final Score = (CF_WEIGHT × CF score) + (CBF_WEIGHT × CBF score)

    Strategy:
      1. Get normalised CF scores for all unrated items (user-based similarity).
      2. Take the top CF item and fetch CBF similarity scores for all catalogue items.
      3. Fuse: hybrid_score = 0.6 * cf_score + 0.4 * cbf_score.
      4. Return the top-n items, enriched with product metadata.

    Falls back to pure CF if the user has no CF results or CBF scores are unavailable.
    """
    cf_scores = get_cf_scores(user_id)
    if not cf_scores:
        logger.warning("Hybrid: no CF scores for user=%s", user_id)
        return []

    # Identify the top CF item to seed the CBF lookup
    top_cf_asin = max(cf_scores, key=cf_scores.get)
    cbf_scores  = get_cbf_scores(top_cf_asin)

    if not cbf_scores:
        logger.warning("Hybrid: CBF returned nothing for asin=%s — falling back to CF only", top_cf_asin)
        cbf_scores = {}

    # Normalise CBF scores to [0, 1] (cosine similarities are already [0,1] but may vary in range)
    if cbf_scores:
        cbf_max = max(cbf_scores.values())
        cbf_scores = {k: v / cbf_max for k, v in cbf_scores.items()} if cbf_max > 0 else cbf_scores

    # Fuse
    all_asins  = set(cf_scores) | set(cbf_scores)
    combined   = {}
    for asin in all_asins:
        cf_s  = cf_scores.get(asin,  0.0)
        cbf_s = cbf_scores.get(asin, 0.0)
        combined[asin] = CF_WEIGHT * cf_s + CBF_WEIGHT * cbf_s

    # Sort descending and take top-n
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:n]

    logger.info(
        "Hybrid: user=%s  cf_items=%d  cbf_items=%d  merged=%d  returned=%d",
        user_id, len(cf_scores), len(cbf_scores), len(combined), len(ranked),
    )

    return [enrich_product(asin, rank + 1) for rank, (asin, _) in enumerate(ranked)]
