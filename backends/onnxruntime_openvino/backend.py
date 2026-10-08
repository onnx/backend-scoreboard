# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for ONNX Runtime with the OpenVINO Execution Provider.

Like the tract, opencv and tvm backends, each inference call runs in a
short-lived worker process via ``subprocess_runner`` so that a crash only
affects a single test.
"""

import os
import unittest

import numpy as np
from onnx.backend.base import Backend, BackendRep
from subprocess_runner import WorkerError, run_in_subprocess


_TIMEOUT = int(os.getenv("OVEP_TEST_TIMEOUT", "120"))


def _check_released_opsets(model):
    """Skip test if the model uses an unreleased opset version."""
    from onnx import helper

    allow_released_only = os.getenv("ALLOW_RELEASED_ONNX_OPSET_ONLY", "1") == "1"
    if allow_released_only:
        for opset in model.opset_import:
            domain = opset.domain if opset.domain else "ai.onnx"
            key = (domain, opset.version)
            if key not in helper.OP_SET_ID_VERSION_MAP:
                raise unittest.SkipTest(
                    f"Skipping: unreleased opset {domain} v{opset.version}"
                )


def _ort_openvino_worker(model_bytes, inputs):
    """Run ORT + OpenVINO EP inference in an isolated subprocess."""
    try:
        import onnxruntime as ort

        providers = ort.get_available_providers()
        sess = ort.InferenceSession(model_bytes, providers=providers)
        sess.disable_fallback()

        input_names = [inp.name for inp in sess.get_inputs()]
        feed = {}
        if isinstance(inputs, list):
            for name, data in zip(input_names, inputs, strict=False):
                feed[name] = np.asarray(data)
        else:
            if len(input_names) != 1:
                raise WorkerError(f"Model expects {len(input_names)} inputs")
            feed[input_names[0]] = np.asarray(inputs)

        return sess.run(None, feed)
    except (RuntimeError, ValueError, OSError) as e:
        raise WorkerError(f"{type(e).__name__}: {e}") from e


class OrtOpenVinoBackendRep(BackendRep):
    """Runtime representation that runs each inference in a subprocess."""

    def __init__(self, model_bytes):
        """Store serialized model bytes for subprocess execution."""
        self.model_bytes = model_bytes

    def run(self, inputs, **kwargs):
        """Execute inference in a spawned worker process."""
        return run_in_subprocess(
            _ort_openvino_worker,
            (self.model_bytes, inputs),
            timeout=_TIMEOUT,
            name="onnxruntime-openvino",
        )


class OrtOpenVinoBackend(Backend):
    """ONNX backend backed by ONNX Runtime with the OpenVINO EP."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether the model is compatible with this backend."""
        return cls.supports_device(device)

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Serialize the model and return a runnable backend representation."""
        if isinstance(model, (str, bytes)):
            if isinstance(model, bytes):
                model_bytes = model
            else:
                with open(model, "rb") as f:
                    model_bytes = f.read()
        else:
            # ModelProto
            from onnx.checker import check_model

            try:
                model_bytes = model.SerializeToString()
                check_model(model_bytes)
            except (ValueError, RuntimeError, OSError) as e:
                raise unittest.SkipTest(f"Model validation failed: {e}") from e

            _check_released_opsets(model)

        return OrtOpenVinoBackendRep(model_bytes)

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        """Prepare then run a model in one call."""
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        """Return whether the backend supports the given device."""
        return device == "CPU"


prepare = OrtOpenVinoBackend.prepare
run_model = OrtOpenVinoBackend.run_model
supports_device = OrtOpenVinoBackend.supports_device
