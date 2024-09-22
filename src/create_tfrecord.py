# create_tfrecord.py

import tensorflow as tf
from object_detection.utils import dataset_util
import json
import os

def create_tf_example(image_path, annotations, label_map_dict):
    # Read the image
    with tf.io.gfile.GFile(image_path, 'rb') as fid:
        encoded_image = fid.read()
    image = Image.open(image_path)
    width, height = image.size

    filename = os.path.basename(image_path).encode('utf8')

    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for annotation in annotations:
        bbox = annotation['bbox']
        xmins.append(bbox[1])  # xmin
        xmaxs.append(bbox[3])  # xmax
        ymins.append(bbox[0])  # ymin
        ymaxs.append(bbox[2])  # ymax
        class_name = annotation['class_name']
        classes_text.append(class_name.encode('utf8'))
        classes.append(label_map_dict[class_name])

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image),
        'image/format': dataset_util.bytes_feature(b'jpg'),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

def create_tfrecord(image_dir, annotations_dir, output_path, label_map_dict):
    writer = tf.io.TFRecordWriter(output_path)
    for image_file in os.listdir(image_dir):
        if image_file.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(image_dir, image_file)
            annotation_file = os.path.splitext(image_file)[0] + '.json'
            annotation_path = os.path.join(annotations_dir, annotation_file)
            if not os.path.exists(annotation_path):
                continue  # Skip images without annotations

            with open(annotation_path, 'r') as f:
                annotations = json.load(f)

            tf_example = create_tf_example(image_path, annotations, label_map_dict)
            writer.write(tf_example.SerializeToString())
    writer.close()
    
def load_label_map_dict(label_map_path):
    label_map_dict = {}
    with open(label_map_path, 'r') as f:
        for line in f:
            if 'id:' in line:
                class_id = int(line.strip().split(' ')[-1])
            if 'name:' in line:
                class_name = line.strip().split(' ')[-1].strip("'")
                label_map_dict[class_name] = class_id
    return label_map_dict

