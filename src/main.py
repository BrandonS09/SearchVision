from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
from ultralytics import YOLO

from src import search_images, train_model

app = FastAPI()

# Serve static files (like images) from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to handle the main form
@app.get("/", response_class=HTMLResponse)
async def index():
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

# Route to handle the search and display images
@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    api_key = "YOUR_API_KEY"
    search_engine_id = "YOUR_SEARCH_ENGINE_ID"
    images = search_images(query, api_key, search_engine_id)
    
    html_content = f"<html><body><h2>Results for: {query}</h2><form action='/select' method='post'>"
    for image_url in images:
        html_content += f"<img src='{image_url}' width='200'><input type='checkbox' name='selected_images' value='{image_url}'><br>"
    html_content += "<button type='submit'>Select Images</button></form></body></html>"
    return html_content

# Route to handle selected images and scrape for similar images
@app.post("/select", response_class=HTMLResponse)
async def select(selected_images: list[str] = Form(...)):
    similar_images = scrape_similar_images(selected_images)
    
    # Here, you'd train your YOLO model with the selected images
    train_model(similar_images, annotations=[])  # Add appropriate annotations
    
    return "<html><body><h2>Model Training Complete</h2></body></html>"
