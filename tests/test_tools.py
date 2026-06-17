from unittest.mock import MagicMock, patch

from tools import search_listings, suggest_outfit, create_fit_card

# Minimal listing dict reused across tests
SAMPLE_ITEM = {
    "id": "lst_test",
    "title": "Vintage Graphic Tee",
    "description": "A cool vintage graphic tee",
    "category": "tops",
    "style_tags": ["vintage", "graphic tee"],
    "size": "M",
    "condition": "good",
    "price": 22.0,
    "colors": ["white", "black"],
    "brand": None,
    "platform": "depop",
}


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    # Failure mode: no listings match → empty list, no exception
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_search_size_filter():
    # Only items whose size field contains "S" (case-insensitive) should come back
    results = search_listings("top", size="S", max_price=None)
    assert all("s" in item["size"].lower() for item in results)


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def _mock_llm_response(text: str):
    """Return a MagicMock that looks like a Groq chat completion."""
    mock = MagicMock()
    mock.choices[0].message.content = text
    return mock


def test_suggest_outfit_empty_wardrobe():
    # Failure mode: wardrobe has no items → returns general styling advice, no crash
    with patch("tools._get_groq_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = (
            _mock_llm_response("Pair this tee with high-waisted jeans and chunky sneakers.")
        )
        result = suggest_outfit(SAMPLE_ITEM, {"items": []})

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_suggest_outfit_missing_items_key():
    # Failure mode: wardrobe dict has no 'items' key → should not crash
    with patch("tools._get_groq_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = (
            _mock_llm_response("Style this with cropped trousers and loafers.")
        )
        result = suggest_outfit(SAMPLE_ITEM, {})

    assert isinstance(result, str)
    assert len(result.strip()) > 0


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def test_create_fit_card_empty_outfit():
    # Failure mode: empty outfit string → error message string, no exception
    result = create_fit_card("", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower()


def test_create_fit_card_whitespace_outfit():
    # Failure mode: whitespace-only outfit string → error message string, no exception
    result = create_fit_card("   ", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower()
