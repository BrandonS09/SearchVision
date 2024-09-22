# src/convert_to_tflite.py

import tensorflow as tf

def convert_to_tflite(saved_model_dir, output_tflite_path):
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Optional: for optimization
    tflite_model = converter.convert()
    with open(output_tflite_path, 'wb') as f:
        f.write(tflite_model)
