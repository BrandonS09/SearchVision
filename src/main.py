# main.py

import os
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
from dotenv import load_dotenv
import shutil
import subprocess

from src.search_images import search_images
from src.search_most_dissimilar_images import select_most_dissimilar_images
from src.download_images import download_images
from src.create_label_map import create_label_map
from src.create_tfrecord import create_tfrecord, load_label_map_dict
from src.train_model import train_model
from src.convert_to_tflite import convert_to_tflite
from src.auto_annotate_images import auto_annotate_images

# Paths to the directories
images_path = "dataset/train/images"
annotations_path = "dataset/train/annotations"

# Clear the directories on startup
def clear_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

clear_directory(images_path)
clear_directory(annotations_path)

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
download_path = images_path
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
        original_query = query
        images = search_images(query, api_key, search_engine_id)

        # Filter the 9 most dissimilar images
        selected_images = select_most_dissimilar_images(images, 9)

        # Display the images to the user for selection
        html_content = f"<html><body><h2>Select the images that contain the object: {query}</h2><form action='/annotate' method='post'>"
        html_content += f"<input type='hidden' name='original_query' value='{original_query}'>"
        for image_url in selected_images:
            html_content += f"<div><img src='{image_url}' width='200'><br><input type='checkbox' name='selected_images' value='{image_url}'></div>"
        html_content += "<button type='submit'>Proceed to Annotation</button></form></body></html>"
        return html_content
    except Exception as e:
        logger.error(f"Error during image search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/annotate", response_class=HTMLResponse)
async def annotate(
        selected_images: list[str] = Form(...),
        original_query: str = Form(...)):
    try:
        if not selected_images:
            raise HTTPException(status_code=400, detail="No images selected.")

        # Download the selected images
        local_image_paths = download_images(selected_images, download_path)

        # Display images for manual annotation
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
            <input type='hidden' name='original_query' value='{original_query}'>
        """
        for idx, local_image_path in enumerate(local_image_paths):
            image_filename = os.path.basename(local_image_path)
            served_image_path = f"/images/{image_filename}"

            # Ensure each canvas and variable is uniquely named
            html_content += f"""
            <div>
                <h3>Image {idx + 1}</h3>
                <canvas id="canvas_{idx}" width="500" height="400"></canvas>
                <input type="hidden" name="image_names" value="{image_filename}">
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
                        x: startX_{idx} / canvas_{idx}.width,
                        y: startY_{idx} / canvas_{idx}.height,
                        width: (endX_{idx} - startX_{idx}) / canvas_{idx}.width,
                        height: (endY_{idx} - startY_{idx}) / canvas_{idx}.height
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
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error during annotation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/save_annotations", response_class=HTMLResponse)
async def save_annotations(
        request: Request,
        image_names: list[str] = Form(...),
        annotations: list[str] = Form(...),
        original_query: str = Form(...)):
    try:
        # Save the annotations
        for image_name, annotation in zip(image_names, annotations):
            annotation_data = json.loads(annotation)
            # Convert normalized coordinates to absolute values
            image_path = os.path.join(images_path, image_name)
            with Image.open(image_path) as img:
                width, height = img.size
            x_min = annotation_data['x'] * width
            y_min = annotation_data['y'] * height
            x_max = x_min + (annotation_data['width'] * width)
            y_max = y_min + (annotation_data['height'] * height)

            annotation_dict = {
                'class_name': original_query,
                'bbox': [y_min / height, x_min / width, y_max / height, x_max / width],  # Normalized coordinates
                'score': 1.0  # Since these are manual annotations
            }

            annotation_file = os.path.splitext(image_name)[0] + '.json'
            annotation_path = os.path.join(annotations_path, annotation_file)
            with open(annotation_path, 'w') as f:
                json.dump([annotation_dict], f)

        logger.info("Manual annotations saved.")

        # Proceed to training with the manually annotated images
        return await train_initial_model(original_query)
    except Exception as e:
        logger.error(f"Error saving annotations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def train_initial_model(original_query):
    try:
        logger.info("Starting initial model training with manual annotations.")

        # Create label map
        class_names = [original_query]
        label_map_path = 'data/label_map.pbtxt'
        create_label_map(class_names, label_map_path)

        # Load label map dictionary
        label_map_dict = load_label_map_dict(label_map_path)

        # Create TFRecord file from manually annotated images
        tfrecord_path = 'data/train_manual.record'
        create_tfrecord(images_path, annotations_path, tfrecord_path, label_map_dict)

        # Train the initial model
        pipeline_config_path = 'models/my_model/pipeline.config'
        model_dir = 'models/my_model'
        train_model(pipeline_config_path, model_dir, tfrecord_path)

        # Use the trained model to auto-annotate additional images
        logger.info("Auto-annotating additional images.")
        auto_annotate_images(images_path, annotations_path, os.path.join(model_dir, 'saved_model'), label_map_path)

        # Create TFRecord file from the expanded dataset
        tfrecord_full_path = 'data/train_full.record'
        create_tfrecord(images_path, annotations_path, tfrecord_full_path, label_map_dict)

        # Retrain the model on the full dataset
        logger.info("Retraining the model on the full dataset.")
        train_model(pipeline_config_path, model_dir, tfrecord_full_path)

        # Convert the final model to TensorFlow Lite
        saved_model_dir = os.path.join(model_dir, 'exported_model', 'saved_model')
        tflite_output_path = os.path.join(model_dir, 'model.tflite')
        convert_to_tflite(saved_model_dir, tflite_output_path)

        return "<html><body><h2>Model Training Complete. Your TensorFlow Lite model is ready!</h2></body></html>"
    except Exception as e:
        logger.error(f"Error during initial model training: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
