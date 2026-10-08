# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for OpenCV DNN module."""

import os

import numpy as np
from onnx.backend.base import Backend, BackendRep
from subprocess_runner import WorkerError, run_in_subprocess


def _opencv_worker(model_bytes, inputs, input_names, output_names):
    """Load and run an ONNX model via OpenCV DNN in an isolated subprocess."""
    import tempfile

    import cv2

    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        f.write(model_bytes)
        path = f.name
    try:
        net = cv2.dnn.readNetFromONNX(path)
        for name, inp in zip(input_names, inputs, strict=True):
            # Feed each input with its declared ONNX dtype instead of forcing
            # everything to float32, which corrupts non-float inputs such as
            # int64 label/index tensors and boolean masks.
            net.setInput(np.ascontiguousarray(inp), name)
        raw = net.forward(output_names)
        # forward() returns ndarray for single output, list for multiple
        if isinstance(raw, np.ndarray):
            raw = [raw]
        return [np.array(o) for o in raw]
    except (cv2.error, RuntimeError, ValueError, TypeError, OSError) as e:
        raise WorkerError(str(e)) from e
    finally:
        os.unlink(path)


class OpenCVBackendRep(BackendRep):
    """Runtime representation for executing models with OpenCV DNN."""

    def __init__(self, model_bytes, input_names, output_names):
        """Store serialized model bytes and graph I/O names."""
        self.model_bytes = model_bytes
        self.input_names = input_names
        self.output_names = output_names

    def run(self, inputs, **kwargs):
        """Execute inference in a spawned worker process."""
        return run_in_subprocess(
            _opencv_worker,
            (self.model_bytes, inputs, self.input_names, self.output_names),
            timeout=60,
            name="opencv",
        )


class OpenCVBackend(Backend):
    """ONNX backend implementation backed by OpenCV DNN."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether this backend can attempt to handle the model."""
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Serialize the model and return a runnable backend representation."""
        model_bytes = model.SerializeToString()
        # IR < 4 exports list initializers in graph.input too; only the rest are
        # fed at runtime.
        initializers = {init.name for init in model.graph.initializer}
        input_names = [
            inp.name for inp in model.graph.input if inp.name not in initializers
        ]
        output_names = [out.name for out in model.graph.output]
        return OpenCVBackendRep(model_bytes, input_names, output_names)

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        """Prepare then run a model in one call."""
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        """Return whether the backend supports the given device."""
        return device == "CPU"


prepare = OpenCVBackend.prepare
run_model = OpenCVBackend.run_model
supports_device = OpenCVBackend.supports_device
