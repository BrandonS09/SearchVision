# src/tests/test_search_images.py

from src.search_images import search_images


def test_search_images():
    """Test search_images with a sample query."""
    api_key = "YOUR_API_KEY"
    search_engine_id = "YOUR_SEARCH_ENGINE_ID"
    query = "cat"

    results = search_images(query, api_key, search_engine_id)
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(url, str) for url in results)
