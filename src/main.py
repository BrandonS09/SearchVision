import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging

from src.search_images import search_images
from src.train_model import train_model
from src.scrape_similar import scrape_similar_images

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
        api_key = "YOUR_API_KEY"
        search_engine_id = "YOUR_SEARCH_ENGINE_ID"
        images = search_images(query, api_key, search_engine_id)

        if not images:
            return HTMLResponse("<html><body><h2>No images found for the query.</h2></body></html>", status_code=404)

        html_content = f"<html><body><h2>Results for: {query}</h2><form action='/select' method='post'>"
        for image_url in images:
            html_content += f"<img src='{image_url}' width='200'><input type='checkbox' name='selected_images' value='{image_url}'><br>"
        html_content += "<button type='submit'>Select Images</button></form></body></html>"
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

        similar_images = scrape_similar_images(selected_images)

        if not similar_images:
            return HTMLResponse("<html><body><h2>No similar images found.</h2></body></html>", status_code=404)

        # Here, you'd train your YOLO model with the selected images
        # Add appropriate annotations
        train_model(similar_images, annotations=[])

        return "<html><body><h2>Model Training Complete</h2></body></html>"
    except HTTPException as he:
        logger.error(f"HTTP error during image selection: {he}")
        raise he
    except Exception as e:
        logger.error(f"Error during image selection or model training: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
