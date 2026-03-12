# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for Apache TVM (Relay frontend)."""

import multiprocessing as mp

import numpy as np
from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt


def _tvm_worker(model_bytes, inputs, input_names, output_count, result_queue):
    """Compile and run an ONNX model via TVM Relay in an isolated subprocess."""
    import onnx
    import tvm
    from tvm import relay
    from tvm.contrib import graph_executor

    model = onnx.ModelProto()
    model.ParseFromString(model_bytes)
    shape_dict = {
        name: np.asarray(inp).shape
        for name, inp in zip(input_names, inputs, strict=True)
    }
    try:
        mod, params = relay.frontend.from_onnx(model, shape=shape_dict)
        with tvm.transform.PassContext(opt_level=3):
            lib = relay.build(mod, target="llvm", params=params)
        module = graph_executor.GraphModule(lib["default"](tvm.cpu(0)))
        for name, inp in zip(input_names, inputs, strict=True):
            module.set_input(name, np.asarray(inp))
        module.run()
        outputs = [module.get_output(i).numpy() for i in range(output_count)]
        result_queue.put(("ok", outputs))
    except (tvm.TVMError, RuntimeError, ValueError, TypeError, OSError) as e:
        result_queue.put(("error", str(e)))


class TVMBackendRep(BackendRep):
    """Runtime representation for executing models with Apache TVM."""

    def __init__(self, model_bytes, input_names, output_count):
        """Store serialized model bytes and graph I/O metadata."""
        self.model_bytes = model_bytes
        self.input_names = input_names
        self.output_count = output_count

    def run(self, inputs, **kwargs):
        """Compile and execute inference in a spawned worker process."""
        ctx = mp.get_context("spawn")
        q = ctx.Queue()
        p = ctx.Process(
            target=_tvm_worker,
            args=(self.model_bytes, inputs, self.input_names, self.output_count, q),
        )
        p.start()
        p.join(timeout=120)
        if p.is_alive():
            p.terminate()
            p.join()
            raise BackendIsNotSupposedToImplementIt("tvm process timed out")
        if p.exitcode != 0:
            raise BackendIsNotSupposedToImplementIt(
                f"tvm process crashed (exit code {p.exitcode})"
            )
        status, result = q.get_nowait()
        if status == "error":
            raise BackendIsNotSupposedToImplementIt(result)
        return result


class TVMBackend(Backend):
    """ONNX backend implementation backed by Apache TVM."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether this backend can attempt to handle the model."""
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Serialize the model and return a runnable backend representation."""
        model_bytes = model.SerializeToString()
        input_names = [inp.name for inp in model.graph.input]
        output_count = len(model.graph.output)
        return TVMBackendRep(model_bytes, input_names, output_count)

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        """Prepare then run a model in one call."""
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        """Return whether the backend supports the given device."""
        return device == "CPU"


prepare = TVMBackend.prepare
run_model = TVMBackend.run_model
supports_device = TVMBackend.supports_device
