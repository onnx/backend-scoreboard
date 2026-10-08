# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for OpenCV DNN module."""

import multiprocessing as mp
import os
from multiprocessing.connection import wait

import numpy as np
from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt


def _opencv_worker(model_bytes, inputs, input_names, output_names, conn):
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
        conn.send(("ok", [np.array(o) for o in raw]))
    except (cv2.error, RuntimeError, ValueError, TypeError, OSError) as e:
        conn.send(("error", str(e)))
    finally:
        conn.close()
        os.unlink(path)


def _read_result(reader):
    """Receive the worker's result, or None if it exited without sending all of it."""
    try:
        return reader.recv()
    except (EOFError, OSError):
        return None


def _stop_worker(process, finished):
    """Reap the worker, escalating to SIGTERM and then SIGKILL if it does not exit."""
    if finished:
        process.join(timeout=5)  # let the worker clean up and exit on its own
    if process.is_alive():
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join()


class OpenCVBackendRep(BackendRep):
    """Runtime representation for executing models with OpenCV DNN."""

    def __init__(self, model_bytes, input_names, output_names):
        """Store serialized model bytes and graph I/O names."""
        self.model_bytes = model_bytes
        self.input_names = input_names
        self.output_names = output_names

    def run(self, inputs, **kwargs):
        """Execute inference in a spawned worker process."""
        ctx = mp.get_context("spawn")
        reader, writer = ctx.Pipe(duplex=False)
        p = ctx.Process(
            target=_opencv_worker,
            args=(
                self.model_bytes,
                inputs,
                self.input_names,
                self.output_names,
                writer,
            ),
        )
        p.start()
        # With the parent's write end closed, a dead worker shows up as EOF on the
        # reader, and reading before joining keeps a large result from deadlocking.
        writer.close()
        ready = wait([reader, p.sentinel], timeout=60)
        outcome = _read_result(reader) if ready else None
        reader.close()
        _stop_worker(p, finished=bool(ready))
        if not ready:
            raise BackendIsNotSupposedToImplementIt("opencv process timed out")
        if outcome is None:
            raise BackendIsNotSupposedToImplementIt(
                f"opencv process crashed (exit code {p.exitcode})"
            )
        status, result = outcome
        if status == "error":
            raise BackendIsNotSupposedToImplementIt(result)
        return result


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
