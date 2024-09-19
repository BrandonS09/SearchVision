from ultralytics import YOLO
import os


def auto_annotate_images(image_dir, output_dir):
    """
    Automatically annotates images using a pre-trained YOLOv8 model.

    :param image_dir: Directory containing images to annotate.
    :param output_dir: Directory to save the annotations.
    """
    # Load a pre-trained YOLOv8 model for object detection
    model = YOLO('yolov8n.pt')  # Using the YOLOv8 nano model as an example

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each image in the directory
    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)

        # Run the YOLO model on the image to get predictions
        results = model(image_path)

        # Extract predictions (bounding boxes and labels)
        with open(os.path.join(output_dir, image_file.replace('.jpg', '.txt')), 'w') as f:
            for result in results:
                for box in result.boxes.data:
                    class_id = int(box[5])  # Class index
                    # Box coordinates
                    x_center, y_center, width, height = box[0:4].tolist()
                    # Write in YOLO format: <class_id> <x_center> <y_center>
                    # <width> <height>
                    f.write(
                        f"{class_id} {x_center} {y_center} {width} {height}\n")
                print(
                    f"Annotated {image_file} with {len(result.boxes)} objects")
