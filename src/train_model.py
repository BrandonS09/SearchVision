from ultralytics import YOLO

def train_model(data_yaml_path):
    """
    Trains the YOLOv8 model using the annotated dataset.

    :param data_yaml_path: Path to the data.yaml file containing the dataset configuration.
    """
    # Load a pre-trained YOLOv8 model
    model = YOLO('yolov8n.pt')  # Using YOLOv8 nano model as an example

    # Train the model using the data.yaml file
    model.train(data=data_yaml_path, epochs=50)

    # Save the trained model
    model.save('yolov8_trained_model.pt')
