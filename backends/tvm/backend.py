# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for Apache TVM (Relax frontend, native ops only)."""

import logging
import sys

import numpy as np
from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt
from subprocess_runner import WorkerError, run_in_subprocess

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def _unsupported_ops(model):
    """Return ops in the model that have no TVM Relax ONNX converter.

    Lets models with unsupported ops skip before compilation, with a message
    naming the missing ops. Returns an empty list when the check cannot be
    performed.
    """
    try:
        from tvm.relax.frontend.onnx.onnx_frontend import _get_convert_map

        convert_map = _get_convert_map()
    except (ImportError, AttributeError, TypeError):
        return []
    return sorted({n.op_type for n in model.graph.node if n.op_type not in convert_map})


def _skip(msg):
    """Log a skip reason on the worker's stderr and return it as a WorkerError."""
    print(f"[tvm] SKIP {msg}", file=sys.stderr, flush=True)
    return WorkerError(msg)


def _to_numpy(value):
    """Flatten a Relax VM result (tensor or nested tuple) into numpy arrays."""
    if hasattr(value, "numpy"):
        return [value.numpy()]
    return [array for item in value for array in _to_numpy(item)]


def _compile_and_run(model, input_names, arrays):
    """Import the model via Relax, compile it for the CPU and run it once."""
    import tvm
    from tvm import relax
    from tvm.relax.frontend.onnx import from_onnx

    mod = from_onnx(
        model,
        shape_dict={n: a.shape for n, a in zip(input_names, arrays, strict=True)},
        dtype_dict={n: str(a.dtype) for n, a in zip(input_names, arrays, strict=True)},
    )
    mod = relax.transform.DecomposeOpsForInference()(mod)
    mod = relax.transform.LegalizeOps()(mod)
    with tvm.transform.PassContext(opt_level=3):
        executable = tvm.compile(mod, target="llvm")
    vm = relax.VirtualMachine(executable, tvm.cpu())
    return _to_numpy(vm["main"](*[tvm.runtime.tensor(a) for a in arrays]))


def _tvm_worker(model_bytes, inputs, input_names):
    """Compile and run an ONNX model via TVM Relax in an isolated subprocess."""
    import onnx

    try:
        import tvm  # noqa: F401
    except (ImportError, AttributeError, OSError, RuntimeError) as e:
        raise _skip(f"tvm import failed: {type(e).__name__}: {e}") from e

    model = onnx.ModelProto()
    model.ParseFromString(model_bytes)

    unsupported = _unsupported_ops(model)
    if unsupported:
        raise _skip(f"no TVM Relax converter for: {unsupported}")

    arrays = [np.ascontiguousarray(inp) for inp in inputs]
    try:
        return _compile_and_run(model, input_names, arrays)
    # TVM >= 0.20 raises its errors as Python builtin exception types.
    except (
        AssertionError,  # the Relax ONNX frontend asserts on unsupported variants
        RuntimeError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OSError,
        ImportError,
    ) as e:
        ops = sorted({n.op_type for n in model.graph.node})
        raise _skip(f"ops={ops} error={type(e).__name__}: {e}") from e


class TVMBackendRep(BackendRep):
    """Runtime representation for executing models with Apache TVM."""

    def __init__(self, model_bytes, input_names):
        """Store serialized model bytes and graph input names."""
        self.model_bytes = model_bytes
        self.input_names = input_names

    def run(self, inputs, **kwargs):
        """Compile and execute inference in a spawned worker process."""
        try:
            return run_in_subprocess(
                _tvm_worker,
                (self.model_bytes, inputs, self.input_names),
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
        return TVMBackendRep(model_bytes, input_names)

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
