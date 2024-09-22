# src/train_model.py

import os
from object_detection.utils import config_util
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
import tensorflow as tf
import subprocess

def train_model(pipeline_config_path, model_dir):
    # Load and possibly modify the pipeline config
    # (if needed, but since we edited it manually, we can skip this)

    # Ensure paths are absolute
    pipeline_config_path = os.path.abspath(pipeline_config_path)
    model_dir = os.path.abspath(model_dir)

    # Construct the command to run
    command = [
        'python',
        'models\\research\\object_detection\\model_main_tf2.py',
        f'--pipeline_config_path={pipeline_config_path}',
        f'--model_dir={model_dir}',
        '--alsologtostderr'
    ]

    # Run the command
    subprocess.run(command, shell=True)
