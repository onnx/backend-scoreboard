import onnx
import ngraph as ng
import numpy as np

from ngraph.impl import onnx_import
from ngraph_onnx.onnx_importer.importer import import_onnx_model

# Import ONNX and load an ONNX file from disk
onnx_protobuf = onnx.load('/root/models/resnet50/model.onnx')

# Convert ONNX model to an ngraph model
ng_function = import_onnx_model(onnx_protobuf)

runtime = ng.runtime(backend_name='CPU')
resnet_on_cpu = runtime.computation(ng_function)

# Load an image (or create a mock as in this example)
picture = np.ones([1, 3, 224, 224], dtype=np.float32)

# Run computation on the picture:
resnet_on_cpu(picture)
# output = prepare(onnx_model).run(picture) # Run the loaded model
