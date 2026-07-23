# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for RTen, executed via a local Rust bridge runner."""

import numpy as np
from onnx import TensorProto
from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt

from rten_bridge import run_model as _bridge_run_model

_TENSOR_TYPE_TO_NP_DTYPE = {
    TensorProto.FLOAT: np.float32,
    TensorProto.FLOAT16: np.float16,
    TensorProto.DOUBLE: np.float64,
    TensorProto.INT8: np.int8,
    TensorProto.INT16: np.int16,
    TensorProto.INT32: np.int32,
    TensorProto.INT64: np.int64,
    TensorProto.UINT8: np.uint8,
    TensorProto.UINT16: np.uint16,
    TensorProto.UINT32: np.uint32,
    TensorProto.UINT64: np.uint64,
    TensorProto.BOOL: np.bool_,
}

# Element types with no native representation in RTen's Value/serialization
# layer (sub-byte packed ints and non-IEEE float formats). Without this check
# these silently round-trip as raw bit patterns instead of failing loudly.
_UNSUPPORTED_ELEM_TYPES = {
    TensorProto.BFLOAT16,
    TensorProto.FLOAT8E4M3FN,
    TensorProto.FLOAT8E4M3FNUZ,
    TensorProto.FLOAT8E5M2,
    TensorProto.FLOAT8E5M2FNUZ,
    TensorProto.INT4,
    TensorProto.UINT4,
}


def _check_tensor_io_supported(value_info):
    """Raise if a graph input/output isn't a plain, supported-dtype tensor."""
    if value_info.type.WhichOneof("value") != "tensor_type":
        raise BackendIsNotSupposedToImplementIt(
            f"'{value_info.name}' is not a plain tensor (RTen bridge only "
            "supports tensor inputs/outputs, not sequences/optionals/maps)"
        )
    elem_type = value_info.type.tensor_type.elem_type
    if elem_type in _UNSUPPORTED_ELEM_TYPES:
        raise BackendIsNotSupposedToImplementIt(
            f"'{value_info.name}' has unsupported element type "
            f"{TensorProto.DataType.Name(elem_type)}"
        )


def _graph_io_names(graph):
    """Return (input_names, output_names), skipping initializer-backed inputs.

    Raises BackendIsNotSupposedToImplementIt if any input/output isn't a
    plain tensor of a type the bridge can round-trip through safetensors.
    """
    initializer_names = {init.name for init in graph.initializer}
    input_names = []
    for vi in graph.input:
        if vi.name in initializer_names:
            continue
        _check_tensor_io_supported(vi)
        input_names.append(vi.name)

    output_names = []
    for vi in graph.output:
        _check_tensor_io_supported(vi)
        output_names.append(vi.name)

    return input_names, output_names


def _output_dtypes(graph):
    """Return a {name: numpy dtype} map for the graph's declared outputs."""
    dtypes = {}
    for vi in graph.output:
        np_dtype = _TENSOR_TYPE_TO_NP_DTYPE.get(vi.type.tensor_type.elem_type)
        if np_dtype is not None:
            dtypes[vi.name] = np_dtype
    return dtypes


class RTenBackendRep(BackendRep):
    """Runs a model through the RTen bridge runner for each inference call."""

    def __init__(self, model_bytes, input_names, output_names, output_dtypes):
        """Store serialized model bytes and run-time I/O metadata."""
        self._model_bytes = model_bytes
        self._input_names = input_names
        self._output_names = output_names
        self._output_dtypes = output_dtypes

    def run(self, inputs, **kwargs):
        """Execute the model via the bridge and cast outputs to their ONNX dtype."""
        try:
            outputs = _bridge_run_model(
                model_bytes=self._model_bytes,
                inputs=inputs,
                input_names=self._input_names,
                output_names=self._output_names,
            )
        except BackendIsNotSupposedToImplementIt:
            raise
        except Exception as exc:  # noqa: BLE001
            raise BackendIsNotSupposedToImplementIt(str(exc)) from exc

        return [
            np.asarray(output).astype(self._output_dtypes[name], copy=False)
            if name in self._output_dtypes
            else np.asarray(output)
            for name, output in zip(self._output_names, outputs, strict=True)
        ]


class RTenBackend(Backend):
    """ONNX backend implementation backed by RTen via the Rust bridge runner."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether this backend can attempt to handle the model."""
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Serialize the model and return a runnable backend representation."""
        input_names, output_names = _graph_io_names(model.graph)
        return RTenBackendRep(
            model.SerializeToString(),
            input_names,
            output_names,
            _output_dtypes(model.graph),
        )

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        """Prepare then run a model in one call."""
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        """Return whether the backend supports the given device."""
        return device == "CPU"


prepare = RTenBackend.prepare
run_model = RTenBackend.run_model
supports_device = RTenBackend.supports_device
