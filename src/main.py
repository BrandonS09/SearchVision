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

# Path for saving and serving static images
download_path = "dataset/train/images"
os.makedirs(download_path, exist_ok=True)

# Serve static files (like images) from the "dataset/train/images" directory
app.mount("/images", StaticFiles(directory=download_path), name="images")

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

@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        images = search_images(query, api_key, search_engine_id)

        # Filter the 9 most dissimilar images
        selected_images = select_most_dissimilar_images(images, 9)

        # Display the images to the user for selection
        html_content = f"<html><body><h2>Select the images that contain the object: {query}</h2><form action='/select' method='post'>"
        for image_url in selected_images:
            html_content += f"<img src='{image_url}' width='200'><input type='checkbox' name='selected_images' value='{image_url}'><br>"
        html_content += "<button type='submit'>Annotate Selected Images</button></form></body></html>"
        return html_content
    except Exception as e:
        logger.error(f"Error during image search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/select", response_class=HTMLResponse)
async def select(selected_images: list[str] = Form(...)):
    try:
        if not selected_images:
            raise HTTPException(status_code=400, detail="No images selected.")
        
        # Step 1: Download the selected images and store their local paths
        local_image_paths = download_images(selected_images, download_path)

        # Step 2: Display the locally downloaded images for annotation
        html_content = """
        <html>
        <body>
            <h2>Annotate the selected images</h2>
            <form action='/save_annotations' method='post'>
        """
        # Loop through the downloaded images (locally stored now)
        for idx, local_image_path in enumerate(local_image_paths):
            image_filename = os.path.basename(local_image_path)  # Extract filename
            served_image_path = f"/images/{image_filename}"  # Serve the image via FastAPI static

            html_content += f"""
            <div>
                <img src="{served_image_path}" id="image_{idx}" width="500">
                <input type="hidden" name="image_urls" value="{served_image_path}">
                <textarea name="annotations" placeholder="Enter annotations for this image"></textarea>
            </div>
            <br>
            """

        html_content += """
            <button type="submit">Save Annotations</button>
            </form>
        </body>
        </html>
        """
        return html_content
    
    except Exception as e:
        logger.error(f"Error during image selection: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/save_annotations", response_class=HTMLResponse)
async def save_annotations(image_urls: list[str] = Form(...), annotations: list[str] = Form(...)):
    try:
        # Step 1: Save the annotations
        annotations_path = "dataset/train/labels"
        os.makedirs(annotations_path, exist_ok=True)

        for image_url, annotation in zip(image_urls, annotations):
            image_name = os.path.basename(image_url)
            annotation_file = os.path.join(annotations_path, image_name.replace('.jpg', '.txt'))

            with open(annotation_file, 'w') as f:
                f.write(annotation)

        # Step 2: After saving annotations, proceed to scrape similar images
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        similar_images = scrape_similar_images(image_urls, api_key, search_engine_id)
        
        # Step 3: Download similar images
        download_images(similar_images, "dataset/train/images")

        # Step 4: Automatically annotate the newly fetched images using a pre-trained YOLO model
        auto_annotate_images("dataset/train/images", annotations_path)

        # Step 5: Train the YOLO model with the annotated dataset
        data_yaml_path = "dataset/data.yaml"
        train_model(data_yaml_path)

        return "<html><body><h2>Model Training Complete. Your YOLOv8 model is ready!</h2></body></html>"
    
    except Exception as e:
        logger.error(f"Error during annotation or model training: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
