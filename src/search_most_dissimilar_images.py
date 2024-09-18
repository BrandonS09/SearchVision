# src/search_most_dissimilar_images.py

import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from PIL import Image
from torchvision import models, transforms
import torch
from src.download_images import download_images  # Import the existing download function

# Load a pre-trained model (e.g., ResNet) for feature extraction
model = models.resnet50(pretrained=True)
model = model.eval()  # Set the model to evaluation mode

# Transformation for input images (resize, normalize, etc.)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def extract_features(image_path):
    """
    Extracts features from an image using a pre-trained model.
    
    :param image_path: Path to the image.
    :return: Feature vector of the image.
    """
    image = Image.open(image_path).convert('RGB')  # Ensure the image is in RGB format
    image_tensor = transform(image).unsqueeze(0)  # Transform and add batch dimension
    with torch.no_grad():
        features = model(image_tensor).numpy().flatten()  # Extract and flatten features
    return features

def select_most_dissimilar_images(image_urls, num_images):
    """
    Selects the most dissimilar images from a list.
    
    :param image_urls: List of image URLs.
    :param num_images: Number of most dissimilar images to select.
    :return: List of the most dissimilar image URLs.
    """
    # Download images to a local directory
    download_path = "temp_images"  # Temporary directory to save downloaded images
    image_paths = download_images(image_urls, download_path=download_path)

    # Extract features from each downloaded image
    features = [extract_features(path) for path in image_paths]

    # Compute the cosine distance matrix between image features
    distance_matrix = cosine_distances(features)

    # Sum the distances for each image and sort them in descending order
    dissimilarity_scores = np.sum(distance_matrix, axis=1)
    most_dissimilar_indices = np.argsort(dissimilarity_scores)[-num_images:]

    # Select the most dissimilar image URLs
    most_dissimilar_images = [image_urls[idx] for idx in most_dissimilar_indices]

    return most_dissimilar_images
