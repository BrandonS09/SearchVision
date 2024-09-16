# Function to train YOLOv8 model
from ultralytics import YOLO


def train_yolov8_model(image_paths, annotations):
    model = YOLO('yolov8n.pt')  # Load a pre-trained YOLOv8 model
    model.train(data={'images': image_paths, 'annotations': annotations}, epochs=50)  # Train the model
    model.save('yolov8_trained_model.pt')
