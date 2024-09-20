from src.search_images import search_images


def scrape_similar_images(
        selected_image_urls,
        api_key,
        search_engine_id,
        num_results_per_image=10,
        total_images_to_download=50):
    similar_images = []
    # Iterate over each selected image
    for url in selected_image_urls:
        query = f"related:{url}"  # Use the URL to find related images
        images = search_images(
            query,
            api_key,
            search_engine_id,
            num_results=num_results_per_image)

        similar_images.extend(images)

        if len(similar_images) >= total_images_to_download:
            break  # Stop if we have enough images

    # Limit the number of images to `total_images_to_download`
    return similar_images[:total_images_to_download]
