import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
from dotenv import load_dotenv

from src import auto_annotate_images
from src.download_images import download_images
from src.search_images import search_images
from src.search_most_dissimilar_images import select_most_dissimilar_images
from src.train_model import train_model
from src.scrape_similar import scrape_similar_images

load_dotenv()
# Initialize the FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Serve static files (like images) from the "static" directory
try:
    static_path = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_path):
        raise FileNotFoundError(
            f"Static directory '{static_path}' does not exist.")
    app.mount("/static", StaticFiles(directory=static_path), name="static")
except Exception as e:
    logger.error(f"Error setting up static files: {e}")

# Route to handle the main form


@app.get("/", response_class=HTMLResponse)
async def index():
    try:
        html_content = """
        <html>
        <body>
            <form action="/search" method="post">
                <input type="text" name="query" placeholder="Search for an item">
                <button type="submit">Search</button>
            </form>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        logger.error(f"Error generating the index page: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Route to handle the search and display images


@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        images = search_images(query, api_key, search_engine_id)

        # Filter the 9 most dissimilar images
        selected_images = select_most_dissimilar_images(images, 9)

        # Display the images to the user for annotation
        html_content = f"<html><body><h2>Select the images that contain the object: {query}</h2><form action='/select' method='post'>"
        for image_url in selected_images:
            html_content += f"<img src='{image_url}' width='200'><input type='checkbox' name='selected_images' value='{image_url}'><br>"
        html_content += "<button type='submit'>Annotate Selected Images</button></form></body></html>"
        return html_content
    except Exception as e:
        logger.error(f"Error during image search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Route to handle selected images and scrape for similar images
@app.post("/select", response_class=HTMLResponse)
async def select(selected_images: list[str] = Form(...)):
    try:
        if not selected_images:
            raise HTTPException(status_code=400, detail="No images selected.")

        # Fetch the API key and Search Engine ID from environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")

        # Ensure the required environment variables are available
        if not api_key or not search_engine_id:
            logger.error("Missing API key or Search Engine ID")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        # Step 1: Download the selected images
        download_path = "dataset/train/images"
        download_images(selected_images, download_path)

        # Step 2: Allow the user to annotate the selected images
        # Here, you might want to display a simple image annotation tool or guide the user to annotate manually
        annotations_path = "dataset/train/labels"
        # Assuming user-annotated images are already saved at `annotations_path`

        # Step 3: Fetch similar images based on user-selected images
        similar_images = scrape_similar_images(selected_images, api_key, search_engine_id)
        download_images(similar_images, download_path)

        # Step 4: Automatically annotate the newly fetched images using a pre-trained YOLO model
        auto_annotate_images(download_path, annotations_path)

        # Step 5: Train the YOLO model with the annotated dataset
        data_yaml_path = "dataset/data.yaml"
        train_model(data_yaml_path)

        return "<html><body><h2>Model Training Complete. Your YOLOv8 model is ready!</h2></body></html>"
    except HTTPException as he:
        logger.error(f"HTTP error during image selection: {he}")
        raise he
    except Exception as e:
        logger.error(f"Error during image selection or model training: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
