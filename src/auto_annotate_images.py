from ultralytics import YOLO
import os
import json


def auto_annotate_images(image_folder, annotations_folder):
    # Load the pre-trained YOLOv8 model
    model = YOLO('yolov8n.pt')

    # Loop through images in the specified folder
    for image_file in os.listdir(image_folder):
        if image_file.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(image_folder, image_file)

            # Check if the image can be opened and processed
            try:
                results = model(image_path)
            except Exception as e:
                print(f"WARNING ⚠️ Unable to process image {image_path}: {e}")
                continue  # Skip to the next image

            # Process the results
            for result in results:
                if result.boxes is not None and result.boxes.xyxy is not None and len(
                        result.boxes) > 0:
                    # Extract bounding boxes in xyxy format
                    boxes = result.boxes.xyxy.cpu().numpy()
                    if len(boxes) == 0:
                        print(f"No annotations found for {image_file}")
                        continue

                    annotations = []

                    # Create the annotation entries
                    for box in boxes:
                        if len(
                                box) >= 4:  # Ensure there are at least 4 elements for xyxy
                            x_min, y_min, x_max, y_max = box[:4]
                            annotation = {
                                "x_min": float(x_min),
                                "y_min": float(y_min),
                                "x_max": float(x_max),
                                "y_max": float(y_max),
                                # Check if confidence exists
                                "confidence": float(box[4]) if len(box) > 4 else None,
                                # Check if class_id exists
                                "class_id": int(box[5]) if len(box) > 5 else None
                            }
                            annotations.append(annotation)

                    # Save the annotations as JSON if any exist
                    if annotations:
                        annotation_filename = os.path.splitext(image_file)[
                            0] + ".json"
                        annotation_path = os.path.join(
                            annotations_folder, annotation_filename)
                        with open(annotation_path, 'w') as f:
                            json.dump(annotations, f)
                        print(
                            f"Saved annotations for {image_file} at {annotation_path}")
                    else:
                        print(f"No valid annotations found for {image_file}")
                else:
                    print(f"No bounding boxes detected for {image_file}")
