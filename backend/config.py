import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "data", "ratings_Electronics.csv")
CACHE_FILE = os.path.join(BASE_DIR, "model_cache.pkl")

MAX_ROWS = 50_000
TOP_N    = 10

CACHE_TIMEOUT = 600

_raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",")]
