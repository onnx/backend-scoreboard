# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for RTen operator-support probing.

This backend does not execute inference. Instead, it checks whether RTen can
convert an ONNX graph using ``rten-convert`` and reports unsupported models as
explicit backend opt-outs. This yields useful operator support signal in the
scoreboard while a full inference path is pending.
"""

from __future__ import annotations

from dataclasses import dataclass

from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt


@dataclass
class _ProbeResult:
    """Result of an RTen convertibility probe."""

    supported: bool
    message: str = ""


def _probe_rten_support(model) -> _ProbeResult:
    """Return whether ``model`` is convertible by RTen.

    A successful conversion indicates likely operator support coverage for the
    model. Conversion failures are surfaced as backend opt-outs.
    """
    try:
        from rten_convert.converter import (
            Metadata,
            graph_from_onnx_graph,
            serialize_model,
        )

        graph = graph_from_onnx_graph(model.graph)
        serialize_model(graph, Metadata(), tensor_data=None)
        return _ProbeResult(supported=True)
    except (RuntimeError, TypeError, ValueError, OSError) as exc:
        return _ProbeResult(supported=False, message=f"RTen conversion failed: {exc}")


class RTenBackendRep(BackendRep):
    """BackendRep carrying convertibility probe results."""

    def __init__(self, probe: _ProbeResult):
        """Store the RTen probe result for this model."""
        self.probe = probe

    def run(self, inputs, **kwargs):
        """Skip inference and surface convertibility result.

        This backend intentionally does not run model execution yet.
        """
        if self.probe.supported:
            raise BackendIsNotSupposedToImplementIt(
                "RTen model conversion succeeded, but inference execution "
                "backend is not implemented yet"
            )
        raise BackendIsNotSupposedToImplementIt(
            self.probe.message
            or "RTen backend execution is not implemented in backend-scoreboard yet"
        )


class RTenBackend(Backend):
    """ONNX backend placeholder for RTen."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        """Return whether this backend can attempt to handle the model."""
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        """Probe convertibility and return backend representation."""
        return RTenBackendRep(_probe_rten_support(model))

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
