# Function to train YOLOv8 model
from ultralytics import YOLO


def train_model(image_paths, annotations):
    model = YOLO('yolov8n.pt')  # Load a pre-trained YOLOv8 model
    # Train the model
    model.train(data={'images': image_paths,
                'annotations': annotations}, epochs=50)
    model.save('yolov8_trained_model.pt')
