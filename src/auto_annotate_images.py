# auto_annotate_images.py

import tensorflow as tf
import numpy as np
from PIL import Image
import os
from object_detection.utils import label_map_util

def load_model(model_dir):
    model = tf.saved_model.load(model_dir)
    return model

def load_label_map(label_map_path):
    return label_map_util.create_category_index_from_labelmap(label_map_path)

def auto_annotate_images(image_folder, annotations_folder, model, category_index):
    for image_file in os.listdir(image_folder):
        if image_file.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(image_folder, image_file)
            image_np = np.array(Image.open(image_path))

            # Prepare the input tensor
            input_tensor = tf.convert_to_tensor(image_np)
            input_tensor = input_tensor[tf.newaxis, ...]

            # Run inference
            detections = model(input_tensor)

            # Process detections
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                          for key, value in detections.items()}
            detections['num_detections'] = num_detections

            # Save annotations in a suitable format (e.g., COCO JSON, Pascal VOC XML)
            save_annotations(image_file, detections, annotations_folder, category_index)
import json

def save_annotations(image_file, detections, annotations_folder, category_index):
    annotations = []
    for i in range(detections['num_detections']):
        score = detections['detection_scores'][i]
        if score >= 0.5:
            bbox = detections['detection_boxes'][i]
            class_id = int(detections['detection_classes'][i])
            class_name = category_index[class_id]['name']

            annotation = {
                'class_name': class_name,
                'bbox': bbox.tolist(),
                'score': float(score)
            }
            annotations.append(annotation)

    # Save annotations to JSON
    annotation_file = os.path.splitext(image_file)[0] + '.json'
    annotation_path = os.path.join(annotations_folder, annotation_file)
    with open(annotation_path, 'w') as f:
        json.dump(annotations, f)
