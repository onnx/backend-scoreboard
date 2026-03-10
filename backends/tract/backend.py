# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for tract (Rust inference engine by Sonos)."""

import os
import tempfile

import numpy as np
import onnx
from onnx.backend.base import Backend, BackendRep


class TractBackendRep(BackendRep):
    def __init__(self, runnable, output_count):
        self.runnable = runnable
        self.output_count = output_count

    def run(self, inputs, **kwargs):
        tract_inputs = [np.asarray(inp) for inp in inputs]
        results = self.runnable.run(tract_inputs)
        return [results[i].to_numpy() for i in range(self.output_count)]


class TractBackend(Backend):
    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        import tract as _tract

        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
            f.write(model.SerializeToString())
            path = f.name

        try:
            runnable = (
                _tract.onnx()
                .model_for_path(path)
                .into_optimized()
                .into_runnable()
            )
        finally:
            os.unlink(path)

        output_count = len(model.graph.output)
        return TractBackendRep(runnable, output_count)

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        return device == "CPU"


prepare = TractBackend.prepare
run_model = TractBackend.run_model
supports_device = TractBackend.supports_device
