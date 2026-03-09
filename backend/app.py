import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from config import CACHE_TIMEOUT, ALLOWED_ORIGINS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

app.config["CACHE_TYPE"]            = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = CACHE_TIMEOUT
cache = Cache(app)


def _get_model():
    import model as _m
    return _m


def _get_cbf():
    import cbf_model as _c
    return _c


def _get_hybrid():
    import hybrid_model as _h
    return _h


def _get_semantic():
    import semantic_model as _s
    return _s


@app.route("/health", methods=["GET"])
def health():
    m   = _get_model()
    cbf = _get_cbf()
    return jsonify({
        "status":          "ok",
        "model_loaded":    m.is_model_loaded(),
        "cbf_loaded":      cbf.is_cbf_loaded(),
    }), 200


@app.route("/search/semantic", methods=["POST"])
def search_semantic():
    t_start = time.perf_counter()

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON.", "code": "missing_body"}), 400

    query = data.get("query", "")
    if not isinstance(query, str) or not query.strip():
        return jsonify({"error": "query must be a non-empty string.", "code": "invalid_query"}), 400

    query = query.strip()

    cache_key = f"sem:{query.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache HIT (semantic) for query='%s'", query)
        return jsonify(cached), 200

    sem  = _get_semantic()
    recs = sem.semantic_search(query)

    response_data = {
        "results": recs,
        "query":   query,
        "count":   len(recs),
    }
    cache.set(cache_key, response_data)

    elapsed = time.perf_counter() - t_start
    logger.info("Semantic search query='%s'  count=%d  time=%.2fs", query, len(recs), elapsed)
    return jsonify(response_data), 200


@app.route("/recommend/hybrid", methods=["POST"])
def recommend_hybrid():
    t_start = time.perf_counter()

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON.", "code": "missing_body"}), 400

    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"error": "user_id is required.", "code": "missing_user_id"}), 400

    if isinstance(user_id, int):
        user_id = str(user_id)

    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "user_id must be a non-empty string.", "code": "invalid_user_id"}), 400

    user_id = user_id.strip()

    cache_key = f"hybrid:{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache HIT (hybrid) for user %s", user_id)
        return jsonify(cached), 200

    h    = _get_hybrid()
    recs = h.hybrid_recommend(user_id)

    if not recs:
        elapsed = time.perf_counter() - t_start
        logger.warning("Hybrid: No results for user=%s (%.2fs)", user_id, elapsed)
        return jsonify({
            "error": f"User '{user_id}' was not found. Use GET /users for valid IDs.",
            "code":  "user_not_found",
        }), 404

    response_data = {
        "recommendations": recs,
        "user_id": user_id,
        "count":   len(recs),
    }
    cache.set(cache_key, response_data)

    elapsed = time.perf_counter() - t_start
    logger.info("Hybrid recommendations for user=%s  count=%d  time=%.2fs", user_id, len(recs), elapsed)
    return jsonify(response_data), 200


@app.route("/users", methods=["GET"])
def users():
    m = _get_model()
    sample = m.get_sample_users(50)
    return jsonify({"users": sample, "count": len(sample)}), 200


@app.route("/recommend", methods=["POST"])
def recommend():
    t_start = time.perf_counter()

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON.", "code": "missing_body"}), 400

    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"error": "user_id is required.", "code": "missing_user_id"}), 400

    if isinstance(user_id, int):
        user_id = str(user_id)

    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "user_id must be a non-empty string.", "code": "invalid_user_id"}), 400

    user_id = user_id.strip()

    cache_key = f"recs:{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache HIT for user %s", user_id)
        return jsonify(cached), 200

    m = _get_model()
    recs = m.recommend_products(user_id)

    if not recs:
        elapsed = time.perf_counter() - t_start
        logger.warning("No recommendations for user=%s (%.2fs)", user_id, elapsed)
        return jsonify({
            "error": f"User '{user_id}' was not found. Use GET /users for valid IDs.",
            "code":  "user_not_found",
        }), 404

    response_data = {
        "recommendations": recs,
        "user_id": user_id,
        "count":   len(recs),
    }
    cache.set(cache_key, response_data)

    elapsed = time.perf_counter() - t_start
    logger.info("Recommendations for user=%s  count=%d  time=%.2fs", user_id, len(recs), elapsed)
    return jsonify(response_data), 200


@app.route("/recommend/content", methods=["POST"])
def recommend_content():
    t_start = time.perf_counter()

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON.", "code": "missing_body"}), 400

    asin = data.get("asin")
    if asin is None:
        return jsonify({"error": "asin is required.", "code": "missing_asin"}), 400

    if not isinstance(asin, str) or not asin.strip():
        return jsonify({"error": "asin must be a non-empty string.", "code": "invalid_asin"}), 400

    asin = asin.strip()

    cache_key = f"cbf:{asin}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache HIT (CBF) for asin %s", asin)
        return jsonify(cached), 200

    cbf  = _get_cbf()
    recs = cbf.recommend_similar(asin)

    if not recs:
        elapsed = time.perf_counter() - t_start
        logger.warning("CBF: No results for asin=%s (%.2fs)", asin, elapsed)
        return jsonify({
            "error": f"ASIN '{asin}' not found. Use POST /recommend to discover valid ASINs.",
            "code":  "asin_not_found",
        }), 404

    response_data = {
        "recommendations": recs,
        "asin":  asin,
        "count": len(recs),
    }
    cache.set(cache_key, response_data)

    elapsed = time.perf_counter() - t_start
    logger.info("CBF recommendations for asin=%s  count=%d  time=%.2fs", asin, len(recs), elapsed)
    return jsonify(response_data), 200


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


if __name__ == "__main__":
    logger.info("Starting Flask development server …")
    app.run(debug=True, port=5000)