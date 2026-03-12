# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper using the official ONNX reference implementation."""

from typing import Any

import numpy as np
from onnx import ModelProto
from onnx.backend.base import Backend, BackendRep, Device, DeviceType
from onnx.reference import ReferenceEvaluator


class ReferenceEvaluatorBackendRep(BackendRep):
    """BackendRep wrapper around ONNX ReferenceEvaluator."""

    def __init__(self, session: ReferenceEvaluator):
        """Initialize the wrapper with a ready reference evaluator session."""
        self._session = session

    def _feeds_from_list(self, inputs: list[np.ndarray]) -> dict[str, np.ndarray]:
        """Build named input feeds from positional inputs."""
        if len(inputs) == len(self._session.input_names):
            return dict(zip(self._session.input_names, inputs, strict=True))

        feeds: dict[str, np.ndarray] = {}
        pos_inputs = 0
        for inp, tshape in zip(
            self._session.input_names,
            self._session.input_types,
            strict=True,
        ):
            if pos_inputs >= len(inputs):
                break
            shape = tuple(d.dim_value for d in tshape.tensor_type.shape.dim)
            if shape == inputs[pos_inputs].shape:
                feeds[inp] = inputs[pos_inputs]
                pos_inputs += 1
        return feeds

    def run(self, inputs, **kwargs):
        """Run inference on a list, array, or dict of input tensors."""
        if isinstance(inputs, np.ndarray):
            inputs = [inputs]

        if isinstance(inputs, list):
            feeds = self._feeds_from_list(inputs)
        elif isinstance(inputs, dict):
            feeds = inputs
        else:
            raise TypeError(f"Unexpected input type {type(inputs)!r}.")

        return self._session.run(None, feeds)


class ReferenceEvaluatorBackend(Backend):
    """ONNX backend implemented via onnx.reference.ReferenceEvaluator."""

    @classmethod
    def is_opset_supported(cls, model):
        """Return whether the backend supports the model opset."""
        return True, ""

    @classmethod
    def supports_device(cls, device: str) -> bool:
        """Return whether the requested device is CPU."""
        d = Device(device)
        return d.type == DeviceType.CPU

    @classmethod
    def create_inference_session(cls, model):
        """Create a ReferenceEvaluator session from a model object."""
        return ReferenceEvaluator(model)

    @classmethod
    def prepare(
        cls, model: Any, device: str = "CPU", **kwargs: Any
    ) -> ReferenceEvaluatorBackendRep:
        """Build and return a backend representation for the provided model."""
        if isinstance(model, ReferenceEvaluator):
            return ReferenceEvaluatorBackendRep(model)
        if isinstance(model, (str, bytes, ModelProto)):
            inf = cls.create_inference_session(model)
            return cls.prepare(inf, device, **kwargs)
        raise TypeError(f"Unexpected type {type(model)} for model.")

    @classmethod
    def run_model(cls, model, inputs, device=None, **kwargs):
        """Prepare and execute model inference in one call."""
        rep = cls.prepare(model, device, **kwargs)
        return rep.run(inputs, **kwargs)


prepare = ReferenceEvaluatorBackend.prepare
run_model = ReferenceEvaluatorBackend.run_model
supports_device = ReferenceEvaluatorBackend.supports_device
