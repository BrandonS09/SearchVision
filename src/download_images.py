# src/download_images.py

import requests  # Make sure this is at the top
import os

def download_images(image_urls, download_path="dataset/train/images"):
    """
    Downloads images from a list of URLs and saves them to the specified directory.

    :param image_urls: List of image URLs to download.
    :param download_path: Directory to save downloaded images.
    """
    print("Starting image download...")  # Debugging statement

    # Ensure the download directory exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Iterate over the image URLs and download each image
    for idx, url in enumerate(image_urls):
        print(f"Attempting to download: {url}")  # Debugging statement
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = os.path.join(download_path, f"image_{idx}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded: {file_path}")
            else:
                print(f"Failed to download {url}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")
