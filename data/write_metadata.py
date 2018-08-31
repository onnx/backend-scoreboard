import csv
import torch
import onnx
import tensorflow as tf

with open('metadata.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(["ONNX", str(onnx.version.version)])
    writer.writerow(["PyTorch/Caffe2", torch.version.__version__])
    writer.writerow(["TensorFlow", tf.__version__])
