# SPDX-License-Identifier: Apache-2.0

"""Python bridge for executing ONNX models with RTen via a local Rust runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence, runtime_checkable
import os
import subprocess
import tempfile

import numpy as np
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt
from safetensors.numpy import load_file, save_file

__bridge_ready__ = True

_RUNNER_DIR = "rten_bridge_runner"
_RUNNER_NAME = "rten_bridge_runner.exe" if os.name == "nt" else "rten_bridge_runner"
_RUNNER_ENV = "RTEN_BRIDGE_BIN"
_CARGO_ENV = "CARGO"


@dataclass(frozen=True, slots=True)
class BridgeRequest:
    """Model data and execution metadata supplied to the bridge."""

    model_bytes: bytes
    inputs: Sequence[Any]
    input_names: Sequence[str]
    output_names: Sequence[str]


@dataclass(frozen=True, slots=True)
class BridgeResult:
    """Outputs returned by the bridge implementation."""

    outputs: Sequence[Any]


@runtime_checkable
class RTenBridge(Protocol):
    """Protocol for a bridge implementation that can execute RTen models."""

    __bridge_ready__: bool

    def run_model(
        self,
        *,
        model_bytes: bytes,
        inputs: Sequence[Any],
        input_names: Sequence[str],
        output_names: Sequence[str],
        **kwargs: Any,
    ) -> Sequence[Any]:
        """Execute a model and return output tensors."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _runner_manifest() -> Path:
    return _repo_root() / _RUNNER_DIR / "Cargo.toml"


def _default_runner_binary() -> Path:
    return _repo_root() / _RUNNER_DIR / "target" / "release" / _RUNNER_NAME


def _resolve_runner_binary() -> Path:
    runner_env = os.getenv(_RUNNER_ENV)
    if runner_env:
        return Path(runner_env)

    runner = _default_runner_binary()
    if runner.exists():
        return runner

    cargo = os.getenv(_CARGO_ENV, "cargo")
    command = [
        cargo,
        "build",
        "--release",
        "--manifest-path",
        str(_runner_manifest()),
    ]
    result = subprocess.run(command, capture_output=True, text=True, cwd=_repo_root())
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip() or "cargo build failed"
        raise BackendIsNotSupposedToImplementIt(
            f"Failed to build RTen bridge runner: {details}"
        )
    if not runner.exists():
        raise BackendIsNotSupposedToImplementIt(
            f"RTen bridge runner was built but not found at {runner}"
        )
    return runner


def _normalize_inputs(inputs: Any, input_names: Sequence[str]) -> dict[str, np.ndarray]:
    if isinstance(inputs, dict):
        return {name: np.asarray(value) for name, value in inputs.items()}

    if isinstance(inputs, np.ndarray):
        inputs = [inputs]

    if not isinstance(inputs, (list, tuple)):
        raise TypeError(f"Unexpected input type {type(inputs)!r}.")

    if len(inputs) != len(input_names):
        raise BackendIsNotSupposedToImplementIt(
            f"RTen bridge expected {len(input_names)} inputs but received {len(inputs)}"
        )

    return {
        name: np.asarray(value)
        for name, value in zip(input_names, inputs, strict=True)
    }


def run_model(
    *,
    model_bytes: bytes,
    inputs: Sequence[Any],
    input_names: Sequence[str],
    output_names: Sequence[str],
    **kwargs: Any,
) -> Sequence[Any]:
    """Execute a model with the local Rust RTen runner and return outputs."""
    del kwargs
    named_inputs = _normalize_inputs(inputs, input_names)
    runner = _resolve_runner_binary()

    with tempfile.TemporaryDirectory(prefix="rten-bridge-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        model_path = tmp_path / "model.onnx"
        inputs_path = tmp_path / "inputs.safetensors"
        outputs_path = tmp_path / "outputs.safetensors"

        model_path.write_bytes(model_bytes)
        save_file(named_inputs, str(inputs_path))

        command = [
            str(runner),
            "--model",
            str(model_path),
            "--inputs",
            str(inputs_path),
            "--outputs",
            str(outputs_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            details = result.stderr.strip() or result.stdout.strip() or "runner failed"
            raise BackendIsNotSupposedToImplementIt(
                f"RTen bridge runner failed: {details}"
            )
        if not outputs_path.exists():
            raise BackendIsNotSupposedToImplementIt(
                "RTen bridge runner did not produce an outputs.safetensors file"
            )

        output_map = load_file(str(outputs_path))
        missing = [name for name in output_names if name not in output_map]
        if missing:
            raise BackendIsNotSupposedToImplementIt(
                f"RTen bridge runner omitted outputs: {missing}"
            )
        return [output_map[name] for name in output_names]
