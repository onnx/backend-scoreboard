# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for Apache TVM (Relay frontend, native ops only)."""

import logging
import sys

import numpy as np
from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt
from subprocess_runner import WorkerError, run_in_subprocess

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def _native_ops_only(model):
    """Return ops in the model that have no native TVM Relay converter.

    Uses TVM's internal converter map to detect ops that would silently fall
    back to the ONNX reference runtime instead of being compiled natively.
    Returns an empty list when the check cannot be performed.
    """
    try:
        from tvm.relay.frontend.onnx import _get_convert_map

        opset = max(
            (x.version for x in model.opset_import if x.domain == ""),
            default=1,
        )
        convert_map = _get_convert_map(opset)
        unsupported = {
            n.op_type for n in model.graph.node if n.op_type not in convert_map
        }
        return sorted(unsupported)
    except (ImportError, AttributeError):
        return []


def _skip(msg):
    """Log a skip reason on the worker's stderr and return it as a WorkerError."""
    print(f"[tvm] SKIP {msg}", file=sys.stderr, flush=True)
    return WorkerError(msg)


def _tvm_worker(model_bytes, inputs, input_names, output_count):
    """Compile and run an ONNX model via TVM Relay in an isolated subprocess."""
    import onnx

    try:
        import tvm
        from tvm import relay
        from tvm.contrib import graph_executor
    except (ImportError, AttributeError, OSError, RuntimeError) as e:
        raise _skip(f"tvm import failed: {type(e).__name__}: {e}") from e

    model = onnx.ModelProto()
    model.ParseFromString(model_bytes)

    unsupported = _native_ops_only(model)
    if unsupported:
        raise _skip(f"no native TVM converter for: {unsupported}")

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
        return [module.get_output(i).numpy() for i in range(output_count)]
    except (
        tvm.TVMError,
        RuntimeError,
        ValueError,
        TypeError,
        OSError,
        ImportError,
    ) as e:
        ops = sorted({n.op_type for n in model.graph.node})
        raise _skip(f"ops={ops} error={type(e).__name__}: {e}") from e


class TVMBackendRep(BackendRep):
    """Runtime representation for executing models with Apache TVM."""

    def __init__(self, model_bytes, input_names, output_count):
        """Store serialized model bytes and graph I/O metadata."""
        self.model_bytes = model_bytes
        self.input_names = input_names
        self.output_count = output_count

    def run(self, inputs, **kwargs):
        """Compile and execute inference in a spawned worker process."""
        try:
            return run_in_subprocess(
                _tvm_worker,
                (self.model_bytes, inputs, self.input_names, self.output_count),
                timeout=120,
                name="tvm",
            )
        except BackendIsNotSupposedToImplementIt as e:
            logger.warning("tvm skip: %s", e)
            raise


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
        # IR < 4 exports list initializers in graph.input too; only the rest are
        # fed at runtime.
        initializers = {init.name for init in model.graph.initializer}
        input_names = [
            inp.name for inp in model.graph.input if inp.name not in initializers
        ]
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
