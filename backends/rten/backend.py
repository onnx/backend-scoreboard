# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper placeholder for RTen.

RTen does not currently expose a drop-in Python ONNX backend module compatible
with ``onnx.backend.test`` in this repository's runtime flow. This wrapper is
added so the backend can be listed in the scoreboard configuration while
explicitly skipping execution until full integration is implemented.
"""

from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt


class RTenBackendRep(BackendRep):
    """BackendRep that marks all executions as unsupported for now."""

    def run(self, inputs, **kwargs):
        """Skip inference until a full RTen execution path is implemented."""
        raise BackendIsNotSupposedToImplementIt(
            "RTen backend execution is not implemented in backend-scoreboard yet"
        )


class RTenBackend(Backend):
    """ONNX backend placeholder for RTen."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether this backend can attempt to handle the model."""
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Return a placeholder backend representation."""
        return RTenBackendRep()

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
