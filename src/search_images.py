import requests
# Function to search for images using Google Custom Search API
def search_images(query, api_key, search_engine_id, num_results=5):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'cx': search_engine_id,
        'key': api_key,
        'searchType': 'image',
        'num': num_results
    }
    response = requests.get(search_url, params=params)
    results = response.json()
    image_urls = [item['link'] for item in results.get('items', [])]
    return image_urls