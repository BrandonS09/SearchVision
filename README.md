# SearchVision

**SearchVision** is a web application built with FastAPI that allows users to search for images, select relevant images, and use web scraping techniques to find similar images. The selected images are then used to train a YOLOv8 (You Only Look Once) model for object detection.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [License](#license)

## Overview

SearchVision is designed to provide a seamless experience for users to perform image searches, select relevant images, and automatically train an object detection model using the selected images. The application leverages Google Custom Search for image retrieval and the YOLOv8 model for real-time object detection training.

## Features

- **Image Search**: Search for images using a query, powered by the Google Custom Search API.
- **Image Selection**: Select images from the search results that match the search criteria.
- **Web Scraping**: Automatically scrape similar images based on the user's selections.
- **Model Training**: Train a YOLOv8 object detection model using the selected and scraped images.
- **Error Handling**: Provides meaningful error messages and logging for smooth user experience.

## Getting Started

To start using SearchVision, visit the deployed web application at:

**[https://your-deployed-domain.com](https://your-deployed-domain.com)**

## Usage

1. **Search for Images**: Enter a search query on the home page to find images related to your query.
2. **Select Images**: Choose the images from the search results that best match your criteria.
3. **Scrape Similar Images**: The application will automatically scrape similar images.
4. **Train Model**: Use the selected and scraped images to train a YOLOv8 object detection model.
5. **View Results**: Monitor the progress and see the results of the model training.

## Technology Stack

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+.
- **YOLOv8**: An object detection model for real-time object detection and tracking.
- **Google Custom Search API**: Provides image search capabilities.
- **BeautifulSoup**: A Python library for web scraping purposes.
- **Uvicorn**: A lightning-fast ASGI server for FastAPI.

## Contributing

We welcome contributions! If you're interested in contributing to SearchVision, please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [YOLOv8](https://github.com/ultralytics/ultralytics)
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

### Contact

If you have any questions or feedback, please open an issue on the repository or contact us at [your-email@example.com](mailto:your-email@example.com).

Thank you for using SearchVision! We hope you enjoy using the app.
