# Function to scrape similar images based on selected images
from src import search_images


def scrape_similar_images(selected_image_urls, api_key, search_engine_id):
    similar_images = []
    for url in selected_image_urls:
        # Use the selected image URL or related terms to search for similar images
        # Here, you can use the original search term or variations of it
        query = f"related:{url}"  # Use the URL to find related images
        images = search_images(query, api_key, search_engine_id, num_results=5)
        similar_images.extend(images)

    return similar_images
