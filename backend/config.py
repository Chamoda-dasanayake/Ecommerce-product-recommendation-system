"""
config.py — Central configuration for the recommendation backend.
Adjust these values to tune performance / paths.
"""
import os

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "ratings_Electronics.csv")
CACHE_FILE = os.path.join(BASE_DIR, "model_cache.pkl")

# ── Model ──────────────────────────────────────────────────────────────────
MAX_ROWS = 50_000   # rows to load from CSV (reduce if training is slow)
TOP_N    = 10       # default number of recommendations to return

# ── API / Cache ────────────────────────────────────────────────────────────
CACHE_TIMEOUT   = 600          # seconds before a cached response expires (10 min)
ALLOWED_ORIGINS = ["http://localhost:3000"]   # React dev server
