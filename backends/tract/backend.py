# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for tract (Rust inference engine by Sonos)."""

import os

import numpy as np
from onnx.backend.base import Backend, BackendRep
from subprocess_runner import WorkerError, run_in_subprocess


def _tract_worker(model_bytes, inputs, output_count):
    """Load and run a tract model in an isolated subprocess."""
    import tempfile

    import tract as _tract

    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        f.write(model_bytes)
        path = f.name
    try:
        runnable = _tract.onnx().load(path).into_model().into_runnable()
        tract_inputs = [np.asarray(inp) for inp in inputs]
        results = runnable.run(tract_inputs)
        return [results[i].to_numpy() for i in range(output_count)]
    except (RuntimeError, ValueError, TypeError, OSError) as e:
        raise WorkerError(str(e)) from e
    finally:
        os.unlink(path)


class TractBackendRep(BackendRep):
    """Runtime representation for executing models with tract."""

    def __init__(self, model_bytes, output_count):
        """Store serialized model bytes and expected output count."""
        self.model_bytes = model_bytes
        self.output_count = output_count

    def run(self, inputs, **kwargs):
        """Execute inference in a spawned worker process."""
        return run_in_subprocess(
            _tract_worker,
            (self.model_bytes, inputs, self.output_count),
            timeout=60,
            name="tract",
        )


class TractBackend(Backend):
    """ONNX backend implementation backed by tract."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether this backend can attempt to handle the model."""
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Serialize the model and return a runnable backend representation."""
        model_bytes = model.SerializeToString()
        output_count = len(model.graph.output)
        return TractBackendRep(model_bytes, output_count)

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        """Prepare then run a model in one call."""
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        """Return whether the backend supports the given device."""
        return device == "CPU"


prepare = TractBackend.prepare
run_model = TractBackend.run_model
supports_device = TractBackend.supports_device
