# src/tests/test_scrape_similar.py

from src.scrape_similar import scrape_similar_images

def test_scrape_similar_images():
    """Test scrape_similar_images with a sample image URL."""
    selected_image_urls = ["http://example.com/image1.jpg"]

    results = scrape_similar_images(selected_image_urls)
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(url, str) for url in results)
