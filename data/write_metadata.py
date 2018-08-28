import csv
import torch
import onnx

with open('metadata.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(["ONNX", str(onnx.version.version)])
    writer.writerow(["PyTorch/Caffe2", torch.version.__version__])
