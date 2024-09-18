import requests

def search_images(query, api_key, search_engine_id):
    """
    Searches for images based on the query using Google Custom Search JSON API.

    :param query: Search query.
    :param api_key: Google API key.
    :param search_engine_id: Custom Search Engine ID.
    :return: List of image URLs.
    """
    # Construct the search URL
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}&searchType=image"

    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            # Log the full response to debug
            print("Search response data:", data)

            # Extract image URLs from search results
            image_urls = [item["link"] for item in data.get("items", [])]

            # Log extracted image URLs
            print("Extracted image URLs:", image_urls)
            
            return image_urls
        else:
            print(f"Failed to fetch images: Status code {response.status_code}, Response: {response.text}")
            return []
    except Exception as e:
        print(f"Error during image search: {e}")
        return []
