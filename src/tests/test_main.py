# src/tests/test_main.py

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_index():
    """Test the index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Search for an item" in response.text


def test_search_endpoint():
    """Test the search endpoint with a sample query."""
    response = client.post("/search", data={"query": "cat"})
    assert response.status_code == 200
    assert "Results for: cat" in response.text


def test_select_endpoint():
    """Test the select endpoint with a sample selection."""
    response = client.post(
        "/select", data={"selected_images": ["http://example.com/image1.jpg"]})
    assert response.status_code == 200
    assert "Model Training Complete" in response.text
