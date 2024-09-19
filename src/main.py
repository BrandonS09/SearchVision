import json
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

# Route to handle selected images and annotation


@app.post("/select", response_class=HTMLResponse)
async def select(selected_images: list[str] = Form(...)):
    try:
        if not selected_images:
            raise HTTPException(status_code=400, detail="No images selected.")
        
        # Step 1: Download the selected images
        download_path = "dataset/train/images"
        download_images(selected_images, download_path)

        # Step 2: Redirect to the annotation page for manual annotation
        html_content = """
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
        </head>
        <body>
            <h2>Annotate the selected images</h2>
            <form action='/save_annotations' method='post'>
        """
        # Generate canvas and images for each selected image
        for idx, image_url in enumerate(selected_images):
            html_content += f"""
            <div>
                <p>Image URL: {image_url}</p>
                <canvas id="canvas_{idx}" width="500" height="500" style="border:1px solid black;"></canvas>
                <input type="hidden" name="image_urls" value="{image_url}">
                <input type="hidden" id="annotation_{idx}" name="annotations" value="">
            </div>
            <br>
            <script>
                // Initialize Fabric.js canvas
                var canvas = new fabric.Canvas('canvas_{idx}');
                
                // Attempt to load the image from the URL
                fabric.Image.fromURL('{image_url}', function(img) {{
                    if (img) {{
                        img.set({{ left: 0, top: 0, scaleX: canvas.width / img.width, scaleY: canvas.height / img.height }});
                        canvas.add(img);
                    }} else {{
                        alert('Failed to load image: {image_url}');
                    }}
                }}, {{ crossOrigin: 'anonymous' }});
                
                var rect, isDown, origX, origY;
                canvas.on('mouse:down', function(o) {{
                    isDown = true;
                    var pointer = canvas.getPointer(o.e);
                    origX = pointer.x;
                    origY = pointer.y;
                    rect = new fabric.Rect({{
                        left: origX, top: origY, originX: 'left', originY: 'top',
                        width: pointer.x - origX, height: pointer.y - origY,
                        fill: 'rgba(255,0,0,0.3)', stroke: 'red', strokeWidth: 2
                    }});
                    canvas.add(rect);
                }});
                canvas.on('mouse:move', function(o) {{
                    if (!isDown) return;
                    var pointer = canvas.getPointer(o.e);
                    rect.set({{ width: pointer.x - origX, height: pointer.y - origY }});
                    canvas.renderAll();
                }});
                canvas.on('mouse:up', function(o) {{
                    isDown = false;
                    var coords = {{
                        left: rect.left / canvas.width,
                        top: rect.top / canvas.height,
                        width: rect.width / canvas.width,
                        height: rect.height / canvas.height
                    }};
                    document.getElementById('annotation_{idx}').value = JSON.stringify(coords);
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
async def save_annotations(image_urls: list[str] = Form(...), annotations: list[str] = Form(...)):
    try:
        # Step 1: Save the annotations
        annotations_path = "dataset/train/labels"
        os.makedirs(annotations_path, exist_ok=True)

        for image_url, annotation in zip(image_urls, annotations):
            image_name = image_url.split('/')[-1].split('?')[0]
            annotation_file = os.path.join(
                annotations_path, image_name.replace('.jpg', '.txt'))

            # Save bounding box data as YOLO format (assuming 1 class, class ID is 0)
            bbox = json.loads(annotation)
            with open(annotation_file, 'w') as f:
                f.write(
                    f"0 {bbox['left'] + bbox['width']/2} {bbox['top'] + bbox['height']/2} {bbox['width']} {bbox['height']}\n")

        # Step 2: After saving annotations, proceed to scrape similar images
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        similar_images = scrape_similar_images(
            image_urls, api_key, search_engine_id)

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
