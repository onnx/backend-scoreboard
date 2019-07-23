import onnx

import onnx_tf.backend as backend
import numpy as np

# Load the ONNX model
model = onnx.load('/root/models/resnet50/model.onnx')

# Check that the IR is well formed
onnx.checker.check_model(model)

# Print a human readable representation of the graph
onnx.helper.printable_graph(model.graph)

rep = backend.prepare(model, device='CPU')

picture = np.ones([1, 3, 224, 224], dtype=np.float32)
outputs = rep.run(picture)

print(outputs[0])
