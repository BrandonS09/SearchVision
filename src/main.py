import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
from dotenv import load_dotenv

from src.auto_annotate_images import auto_annotate_images
from src.download_images import download_images
from src.search_images import search_images
from src.search_most_dissimilar_images import select_most_dissimilar_images
from src.train_model import train_model
from src.scrape_similar import scrape_similar_images
# Import your create_data_yaml function
from src.create_data_yaml import create_data_yaml
import shutil

# Paths to the directories
images_path = "dataset/train/images"
labels_path = "dataset/train/labels"

# Clear the directories on startup


def clear_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)  # Remove the directory and its contents
    os.makedirs(path)  # Recreate the directory


# Clear the images and labels directories
clear_directory(images_path)
clear_directory(labels_path)

load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Set up logging
log_file_path = os.path.join(os.getcwd(), 'app_logs.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
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
        original_query = query  # Store original query
        images = search_images(query, api_key, search_engine_id)

        # Filter the 9 most dissimilar images
        selected_images = select_most_dissimilar_images(images, 9)

        # Display the images to the user for selection and pass
        # `original_query`
        html_content = f"<html><body><h2>Select the images that contain the object: {query}</h2><form action='/select' method='post'>"
        # Pass original query
        html_content += f"<input type='hidden' name='original_query' value='{original_query}'>"
        for image_url in selected_images:
            html_content += f"<img src='{image_url}' width='200'><input type='checkbox' name='selected_images' value='{image_url}'><br>"
        html_content += "<button type='submit'>Annotate Selected Images</button></form></body></html>"
        return html_content
    except Exception as e:
        logger.error(f"Error during image search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/select", response_class=HTMLResponse)
async def select(
        selected_images: list[str] = Form(...),
        original_query: str = Form(...)):
    try:
        if not selected_images:
            raise HTTPException(status_code=400, detail="No images selected.")

        # Step 1: Download the selected images and store their local paths
        local_image_paths = download_images(selected_images, download_path)

        # Step 2: Display the locally downloaded images for annotation using
        # pure HTML5 Canvas
        html_content = f"""
        <html>
        <head>
            <style>
                canvas {{
                    border: 1px solid black;
                }}
            </style>
        </head>
        <body>
            <h2>Annotate the selected images</h2>
            <form action='/save_annotations' method='post'>
            <input type='hidden' name='original_query' value='{original_query}'>  <!-- Keep passing original_query -->
        """
        for idx, local_image_path in enumerate(local_image_paths):
            image_filename = os.path.basename(local_image_path)
            served_image_path = f"/images/{image_filename}"

            # Ensure each canvas and variable is uniquely named to avoid
            # conflict
            html_content += f"""
            <div>
                <h3>Image {idx + 1}</h3>
                <canvas id="canvas_{idx}" width="500" height="400"></canvas>
                <input type="hidden" name="image_urls" value="{served_image_path}">
                <input type="hidden" id="annotation_{idx}" name="annotations">
                <br><br>
            </div>
            <script>
                var canvas_{idx} = document.getElementById('canvas_{idx}');
                var ctx_{idx} = canvas_{idx}.getContext('2d');
                var img_{idx} = new Image();
                img_{idx}.src = '{served_image_path}';
                img_{idx}.onload = function() {{
                    ctx_{idx}.drawImage(img_{idx}, 0, 0, canvas_{idx}.width, canvas_{idx}.height);
                }};

                var isDown_{idx} = false;
                var startX_{idx}, startY_{idx}, endX_{idx}, endY_{idx};

                canvas_{idx}.addEventListener('mousedown', function(e) {{
                    isDown_{idx} = true;
                    var rect = canvas_{idx}.getBoundingClientRect();
                    startX_{idx} = e.clientX - rect.left;
                    startY_{idx} = e.clientY - rect.top;
                }});

                canvas_{idx}.addEventListener('mousemove', function(e) {{
                    if (!isDown_{idx}) return;
                    var rect = canvas_{idx}.getBoundingClientRect();
                    var currentX = e.clientX - rect.left;
                    var currentY = e.clientY - rect.top;

                    // Redraw the image to clear the previous rectangle
                    ctx_{idx}.clearRect(0, 0, canvas_{idx}.width, canvas_{idx}.height);
                    ctx_{idx}.drawImage(img_{idx}, 0, 0, canvas_{idx}.width, canvas_{idx}.height);

                    // Draw the current rectangle
                    ctx_{idx}.beginPath();
                    ctx_{idx}.rect(startX_{idx}, startY_{idx}, currentX - startX_{idx}, currentY - startY_{idx});
                    ctx_{idx}.strokeStyle = 'red';
                    ctx_{idx}.lineWidth = 2;
                    ctx_{idx}.stroke();
                }});

                canvas_{idx}.addEventListener('mouseup', function(e) {{
                    isDown_{idx} = false;
                    var rect = canvas_{idx}.getBoundingClientRect();
                    endX_{idx} = e.clientX - rect.left;
                    endY_{idx} = e.clientY - rect.top;

                    // Save the rectangle coordinates as the annotation
                    document.getElementById('annotation_{idx}').value = JSON.stringify({{
                        x: startX_{idx},
                        y: startY_{idx},
                        width: endX_{idx} - startX_{idx},
                        height: endY_{idx} - startY_{idx}
                    }});
                }});
            </script>
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
async def save_annotations(
        image_urls: list[str] = Form(...),
        annotations: list[str] = Form(...),
        original_query: str = Form(...)):
    try:
        # Save the annotations as JSON containing bounding box coordinates
        annotations_path = "dataset/train/labels"
        os.makedirs(annotations_path, exist_ok=True)

        for image_url, annotation in zip(image_urls, annotations):
            image_name = os.path.basename(image_url)
            annotation_file = os.path.join(
                annotations_path, image_name.replace(
                    '.jpg', '.json'))

            with open(annotation_file, 'w') as f:
                f.write(annotation)

        logger.info("Annotations saved, proceeding to scrape similar images")

        # Scrape similar images
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")

        logger.info("Starting to scrape similar images")
        similar_images = scrape_similar_images(
            image_urls,
            original_query,
            api_key,
            search_engine_id,
            num_results_per_image=20,
            total_images_to_download=50)
        logger.info(f"Scraped similar images: {similar_images}")

        # Download similar images
        logger.info("Downloading similar images")
        download_images(similar_images, "dataset/train/images")
        logger.info("Similar images downloaded successfully")

        # Auto-annotate the newly fetched images
        logger.info("Auto-annotating similar images")
        auto_annotate_images("dataset/train/images", annotations_path)
        logger.info("Auto-annotation completed successfully")

        # Create the data.yaml file based on the annotations
        logger.info("Creating data.yaml file")
        create_data_yaml(annotations_path)

        # Train the YOLO model with the annotated dataset
        logger.info("Starting model training")
        data_yaml_path = "dataset/data.yaml"
        train_model(data_yaml_path)
        logger.info("Model training completed successfully")

        return "<html><body><h2>Model Training Complete. Your YOLOv8 model is ready!</h2></body></html>"

    except Exception as e:
        logger.error(f"Error during annotation or model training: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
