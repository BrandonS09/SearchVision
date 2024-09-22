# src/search_most_dissimilar_images.py

import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import ResNet50, resnet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import os
from src.download_images import download_images

# Load a pre-trained model (e.g., ResNet50) for feature extraction
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(image_path):
    """
    Extracts features from an image using a pre-trained model.

    :param image_path: Path to the image.
    :return: Feature vector of the image.
    """
    try:
        img = image.load_img(image_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        features = model.predict(x)
        features = features.flatten()
        return features
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return None

def select_most_dissimilar_images(image_urls, num_images):
    """
    Selects the most dissimilar images from a list.

    :param image_urls: List of image URLs.
    :param num_images: Number of most dissimilar images to select.
    :return: List of the most dissimilar image URLs.
    """
    # Download images to a local directory
    # Now returns a mapping from URLs to paths
    url_to_path = download_images(image_urls, download_path="dataset/train/images")

    # Validate that images were downloaded
    if not url_to_path:
        print("No images were downloaded.")
        return []

    # Extract features from each downloaded image
    features = []
    valid_urls = []
    for url, path in url_to_path.items():
        feature = extract_features(path)
        if feature is not None:
            features.append(feature)
            valid_urls.append(url)

    # Ensure there are enough features to proceed
    if len(features) < num_images:
        print("Not enough images to select the most dissimilar ones.")
        return valid_urls  # Return as many images as available

    # Convert features list to a numpy array
    features = np.array(features)

    # Compute the cosine distance matrix between image features
    distance_matrix = cosine_distances(features)

    # Sum the distances for each image and sort them in descending order
    dissimilarity_scores = np.sum(distance_matrix, axis=1)
    most_dissimilar_indices = np.argsort(dissimilarity_scores)[-num_images:]

    # Select the most dissimilar image URLs
    most_dissimilar_images = [valid_urls[idx] for idx in most_dissimilar_indices]

    return most_dissimilar_images
