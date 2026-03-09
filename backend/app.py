
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from config import CACHE_TIMEOUT, ALLOWED_ORIGINS

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App & extensions ───────────────────────────────────────────────────────
app = Flask(__name__)

# CORS — only allow our React dev server
CORS(app, origins=ALLOWED_ORIGINS)

# In-memory response cache
app.config["CACHE_TYPE"]             = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"]  = CACHE_TIMEOUT
cache = Cache(app)

# ── Lazy-import model (avoids heavy load at import time of tests) ──────────
def _get_model():
    """Import CF model functions on first use."""
    import model as _m
    return _m


def _get_cbf():
    """Import CBF model functions on first use."""
    import cbf_model as _c
    return _c


# ════════════════════════════════════════════════════════════════════════════
# Routes
# ════════════════════════════════════════════════════════════════════════════

@app.route("/health", methods=["GET"])
def health():
    """
    Liveness probe.
    Returns 200 with model_loaded=True once the CF model is ready,
    and cbf_loaded=True once the CBF model is ready.
    """
    m   = _get_model()
    cbf = _get_cbf()
    return jsonify({
        "status":     "ok",
        "model_loaded": m.is_model_loaded(),
        "cbf_loaded":   cbf.is_cbf_loaded(),
    }), 200


@app.route("/users", methods=["GET"])
def users():
    """
    Return a sample of valid user IDs from the training dataset.
    The frontend can use these to populate a dropdown.
    """
    m = _get_model()
    sample = m.get_sample_users(50)
    return jsonify({"users": sample, "count": len(sample)}), 200


@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Body: { "user_id": "<string>" }
    Returns: { "recommendations": ["prod1", ...], "user_id": "...", "count": N }
    """
    t_start = time.perf_counter()

    # ── 1. Parse body ────────────────────────────────────────────────────────
    data = request.get_json(silent=True)
    if data is None:
        logger.warning("Request body is missing or not valid JSON.")
        return jsonify({
            "error": "Request body must be JSON.",
            "code": "missing_body",
        }), 400

    user_id = data.get("user_id")

    # ── 2. Validate ──────────────────────────────────────────────────────────
    if user_id is None:
        return jsonify({
            "error": "user_id is required.",
            "code": "missing_user_id",
        }), 400

    # Accept both string and integer user_id (convert int → str)
    if isinstance(user_id, int):
        user_id = str(user_id)

    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({
            "error": "user_id must be a non-empty string.",
            "code": "invalid_user_id",
        }), 400

    user_id = user_id.strip()

    # ── 3. Check cache ───────────────────────────────────────────────────────
    cache_key = f"recs:{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache HIT for user %s", user_id)
        return jsonify(cached), 200

    # ── 4. Get recommendations ───────────────────────────────────────────────
    m = _get_model()
    recs = m.recommend_products(user_id)

    if recs is None or len(recs) == 0:
        elapsed = time.perf_counter() - t_start
        logger.warning("No recommendations found for user=%s (%.2fs)", user_id, elapsed)
        return jsonify({
            "error": (
                f"User '{user_id}' was not found in the dataset. "
                "Use GET /users to retrieve valid user IDs."
            ),
            "code": "user_not_found",
        }), 404

    # ── 5. Cache & return ────────────────────────────────────────────────────
    response_data = {
        "recommendations": recs,   # list of enriched product dicts
        "user_id": user_id,
        "count": len(recs),
    }
    cache.set(cache_key, response_data)

    elapsed = time.perf_counter() - t_start
    logger.info("Recommendations served for user=%s  count=%d  time=%.2fs",
                user_id, len(recs), elapsed)

    return jsonify(response_data), 200


@app.route("/recommend/content", methods=["POST"])
def recommend_content():
    """
    Content-Based Filtering endpoint.
    Body:   { "asin": "<string>" }
    Returns: { "recommendations": [...], "asin": "...", "count": N }
    """
    t_start = time.perf_counter()

    # ── 1. Parse body ────────────────────────────────────────────────────────
    data = request.get_json(silent=True)
    if data is None:
        logger.warning("CBF request body is missing or not valid JSON.")
        return jsonify({
            "error": "Request body must be JSON.",
            "code":  "missing_body",
        }), 400

    asin = data.get("asin")

    # ── 2. Validate ──────────────────────────────────────────────────────────
    if asin is None:
        return jsonify({
            "error": "asin is required.",
            "code":  "missing_asin",
        }), 400

    if not isinstance(asin, str) or not asin.strip():
        return jsonify({
            "error": "asin must be a non-empty string.",
            "code":  "invalid_asin",
        }), 400

    asin = asin.strip()

    # ── 3. Check cache ───────────────────────────────────────────────────────
    cache_key = f"cbf:{asin}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache HIT (CBF) for asin %s", asin)
        return jsonify(cached), 200

    # ── 4. Get similar products ──────────────────────────────────────────────
    cbf  = _get_cbf()
    recs = cbf.recommend_similar(asin)

    if not recs:
        elapsed = time.perf_counter() - t_start
        logger.warning("CBF: No results for asin=%s (%.2fs)", asin, elapsed)
        return jsonify({
            "error": (
                f"ASIN '{asin}' was not found in the product catalogue. "
                "Use GET /users then POST /recommend to discover valid ASINs."
            ),
            "code": "asin_not_found",
        }), 404

    # ── 5. Cache & return ────────────────────────────────────────────────────
    response_data = {
        "recommendations": recs,
        "asin":  asin,
        "count": len(recs),
    }
    cache.set(cache_key, response_data)

    elapsed = time.perf_counter() - t_start
    logger.info("CBF recommendations served for asin=%s  count=%d  time=%.2fs",
                asin, len(recs), elapsed)

    return jsonify(response_data), 200


# ════════════════════════════════════════════════════════════════════════════
# Error handlers
# ════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Endpoint not found.", "code": "not_found"}), 404


@app.errorhandler(405)
def method_not_allowed(_e):
    return jsonify({"error": "Method not allowed.", "code": "method_not_allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    logger.exception("Unhandled server error: %s", e)
    return jsonify({"error": "Internal server error.", "code": "server_error"}), 500


# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("Starting Flask development server …")
    app.run(debug=True, port=5000)