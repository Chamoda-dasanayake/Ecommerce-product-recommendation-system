"""
test_app.py — Unit tests for the recommendation API.

Run from the backend directory:
    pytest test_app.py -v
"""

import pytest
import json

import sys
from unittest.mock import MagicMock, patch

# Create a mock model module
_mock_model = MagicMock()
_mock_model.is_model_loaded.return_value = True
_mock_model.get_sample_users.return_value = [
    "A3SGXH7AUHU8GW", "A1D87F6ZCVE5NK", "A1SP9NJP4VVKDA",
]

# Mock enriched product dicts (matches new model.py output shape)
_MOCK_RECS = [
    {
        "asin": "B00004NKIQ", "rank": 1,
        "name": "Sony Pro Headphones", "brand": "Sony",
        "category": "Audio", "emoji": "🎧",
        "price": 129, "rating": 4.5, "match_score": 93,
    },
    {
        "asin": "B000068O48", "rank": 2,
        "name": "Samsung Elite Smartphone", "brand": "Samsung",
        "category": "Mobile", "emoji": "📱",
        "price": 699, "rating": 4.3, "match_score": 88,
    },
    {
        "asin": "B0000C7KH8", "rank": 3,
        "name": "Apple Ultra Laptop", "brand": "Apple",
        "category": "Computers", "emoji": "💻",
        "price": 1199, "rating": 4.7, "match_score": 83,
    },
]

_mock_model.recommend_products.side_effect = lambda uid, **kw: (
    _MOCK_RECS if uid == "A3SGXH7AUHU8GW" else []
)
sys.modules["model"] = _mock_model

# Create a mock cbf_model module
_mock_cbf = MagicMock()
_mock_cbf.is_cbf_loaded.return_value = True
_mock_cbf.recommend_similar.side_effect = lambda asin, **kw: (
    _MOCK_RECS if asin == "B00004NKIQ" else []
)
sys.modules["cbf_model"] = _mock_cbf

import app as flask_app   # import after mock is injected


@pytest.fixture(scope="module")
def client():
    flask_app.app.config["TESTING"] = True
    flask_app.app.config["CACHE_TYPE"] = "SimpleCache"
    with flask_app.app.test_client() as c:
        yield c


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_health_ok(client):
    """GET /health should return 200 and status=ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_users_endpoint(client):
    """GET /users should return a JSON list of user ID strings."""
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "users" in data
    assert isinstance(data["users"], list)
    assert len(data["users"]) > 0
    assert all(isinstance(uid, str) for uid in data["users"])


def test_recommend_missing_body(client):
    """POST /recommend with no body should return 400 missing_body."""
    resp = client.post("/recommend", content_type="application/json", data="")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["code"] == "missing_body"


def test_recommend_missing_user_id(client):
    """POST /recommend with body but no user_id key should return 400."""
    resp = client.post(
        "/recommend",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["code"] == "missing_user_id"


def test_recommend_user_not_found(client):
    """POST /recommend with unknown user_id should return 404 user_not_found."""
    resp = client.post(
        "/recommend",
        data=json.dumps({"user_id": "UNKNOWN_USER_XYZ"}),
        content_type="application/json",
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["code"] == "user_not_found"


def test_recommend_valid_user(client):
    """POST /recommend with a known user_id should return enriched product objects."""
    resp = client.post(
        "/recommend",
        data=json.dumps({"user_id": "A3SGXH7AUHU8GW"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    assert data["user_id"] == "A3SGXH7AUHU8GW"

    # Verify enriched fields are present
    first = data["recommendations"][0]
    for field in ("asin", "rank", "name", "brand", "category", "emoji", "price", "rating", "match_score"):
        assert field in first, f"Missing field: {field}"


# ── CBF Tests ──────────────────────────────────────────────────────────────

def test_cbf_missing_body(client):
    """POST /recommend/content with no body should return 400 missing_body."""
    resp = client.post("/recommend/content", content_type="application/json", data="")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["code"] == "missing_body"


def test_cbf_missing_asin(client):
    """POST /recommend/content with body but no asin key should return 400."""
    resp = client.post(
        "/recommend/content",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["code"] == "missing_asin"


def test_cbf_asin_not_found(client):
    """POST /recommend/content with unknown asin should return 404 asin_not_found."""
    resp = client.post(
        "/recommend/content",
        data=json.dumps({"asin": "UNKNOWN_ASIN_XYZ"}),
        content_type="application/json",
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["code"] == "asin_not_found"


def test_cbf_valid_asin(client):
    """POST /recommend/content with a known asin should return enriched product objects."""
    resp = client.post(
        "/recommend/content",
        data=json.dumps({"asin": "B00004NKIQ"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    assert data["asin"] == "B00004NKIQ"

    # Verify enriched fields are present
    first = data["recommendations"][0]
    for field in ("asin", "rank", "name", "brand", "category", "emoji", "price", "rating", "match_score"):
        assert field in first, f"CBF missing field: {field}"
