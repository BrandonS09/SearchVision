from src.search_images import search_images

def scrape_similar_images(selected_image_urls, original_query, api_key, search_engine_id, num_results_per_image=10, total_images_to_download=50):
    similar_images = []
    
    # Fallback query keywords if the original search fails
    fallback_queries = [f"{original_query} object", f"high quality {original_query}"]

    # Iterate over each selected image and use a descriptive search
    for url in selected_image_urls:
        # Step 1: Use the original query to search for more images
        images = search_images(original_query, api_key, search_engine_id, num_results=num_results_per_image)
        similar_images.extend(images)

        # If we haven't downloaded enough images yet, use fallback queries
        for fallback_query in fallback_queries:
            if len(similar_images) >= total_images_to_download:
                break  # Stop if we have enough images
            
            # Step 2: Perform fallback search
            fallback_images = search_images(fallback_query, api_key, search_engine_id, num_results=num_results_per_image)
            similar_images.extend(fallback_images)

        # Stop if we have downloaded enough images
        if len(similar_images) >= total_images_to_download:
            break

    # Limit the number of images to `total_images_to_download`
    return similar_images[:total_images_to_download]


