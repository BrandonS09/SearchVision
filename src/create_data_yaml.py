import yaml
import os
import json
import logging

logger = logging.getLogger(__name__)


def create_data_yaml(labels_path):
    try:
        classes = set()

        # Iterate over all JSON files in the labels_path to collect class names
        for file_name in os.listdir(labels_path):
            if file_name.endswith('.json'):
                with open(os.path.join(labels_path, file_name), 'r') as f:
                    annotation_data = json.load(f)

                    # Ensure annotation_data is correctly loaded
                    if not annotation_data:
                        logger.warning(
                            f"No data found in {file_name}. Skipping this file.")
                        continue

                    # Check for expected annotation structure
                    if isinstance(annotation_data, list):
                        for item in annotation_data:
                            if isinstance(item, dict) and 'class' in item:
                                classes.add(item['class'])
                    elif isinstance(annotation_data, dict) and 'class' in annotation_data:
                        classes.add(annotation_data['class'])
                    else:
                        logger.warning(
                            f"Unexpected annotation format in {file_name}. Skipping this file.")

        # Convert set to sorted list to maintain a consistent order
        classes_list = sorted(list(classes))

        # Check if classes_list is empty
        if not classes_list:
            raise ValueError(
                "No classes found in annotations. Please check your annotation files.")

        # Prepare the YAML content
        data_yaml = {
            'train': os.path.abspath("dataset/train/images"),
            # Use the same directory if no separate validation set
            'val': os.path.abspath("dataset/train/images"),
            'nc': len(classes_list),
            'names': classes_list
        }

        # Write the data.yaml file
        yaml_path = os.path.join('dataset', 'data.yaml')
        with open(yaml_path, 'w') as yaml_file:
            yaml.dump(data_yaml, yaml_file, default_flow_style=False)

        logger.info(f"data.yaml created successfully at {yaml_path}")

    except Exception as e:
        logger.error(f"Error creating data.yaml: {e}")
        raise
