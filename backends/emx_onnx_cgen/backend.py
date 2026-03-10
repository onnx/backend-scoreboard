# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for emx-onnx-cgen (C code generator)."""

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto
from onnx.backend.base import Backend, BackendRep

_ELEM_TYPE_TO_DTYPE = {
    TensorProto.FLOAT: np.dtype("float32"),
    TensorProto.DOUBLE: np.dtype("float64"),
    TensorProto.INT8: np.dtype("int8"),
    TensorProto.INT16: np.dtype("int16"),
    TensorProto.INT32: np.dtype("int32"),
    TensorProto.INT64: np.dtype("int64"),
    TensorProto.UINT8: np.dtype("uint8"),
    TensorProto.UINT16: np.dtype("uint16"),
    TensorProto.UINT32: np.dtype("uint32"),
    TensorProto.UINT64: np.dtype("uint64"),
    TensorProto.BOOL: np.dtype("bool"),
    TensorProto.FLOAT16: np.dtype("float16"),
}

# In-process cache: model_hash -> compiled executable path
_compile_cache: dict[str, Path] = {}


class EmxBackendRep(BackendRep):
    def __init__(self, executable: Path, output_infos: list[tuple[str, np.dtype]]):
        self.executable = executable
        self.output_infos = output_infos

    def run(self, inputs, **kwargs):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            input_path = f.name
            for inp in inputs:
                f.write(np.asarray(inp).tobytes())

        try:
            result = subprocess.run(
                [str(self.executable), input_path],
                capture_output=True,
                timeout=60,
            )
        finally:
            os.unlink(input_path)

        if result.returncode != 0:
            raise RuntimeError(
                f"Execution failed:\n{result.stderr.decode(errors='replace')}"
            )

        output_json = json.loads(result.stdout.decode())
        outputs_data = output_json.get("outputs", {})

        results = []
        for i, (name, dtype) in enumerate(self.output_infos):
            # Look up by name first, fall back to index order
            key = name if name in outputs_data else list(outputs_data.keys())[i]
            out = outputs_data[key]
            shape = out["shape"]
            data = out["data"]
            arr = np.array(data, dtype=dtype)
            if shape:
                arr = arr.reshape(shape)
            results.append(arr)

        return results


class EmxBackend(Backend):
    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        from emx_onnx_cgen.compiler import Compiler, CompilerOptions

        model_hash = hashlib.md5(model.SerializeToString()).hexdigest()

        if model_hash not in _compile_cache:
            options = CompilerOptions(
                emit_testbench=True,
                testbench_output_format="json",
            )
            try:
                c_code = Compiler(options).compile(model)
            except Exception as e:
                raise RuntimeError(f"C code generation failed: {e}") from e

            tmp_dir = Path(tempfile.mkdtemp(prefix="emx_"))
            c_file = tmp_dir / "model.c"
            exe_file = tmp_dir / "model"
            c_file.write_text(c_code)

            result = subprocess.run(
                ["gcc", "-O2", "-lm", str(c_file), "-o", str(exe_file)],
                capture_output=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"gcc compilation failed:\n{result.stderr.decode(errors='replace')}"
                )

            _compile_cache[model_hash] = exe_file

        output_infos = [
            (out.name, _ELEM_TYPE_TO_DTYPE.get(out.type.tensor_type.elem_type, np.dtype("float32")))
            for out in model.graph.output
        ]
        return EmxBackendRep(_compile_cache[model_hash], output_infos)

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        return device == "CPU"


prepare = EmxBackend.prepare
run_model = EmxBackend.run_model
supports_device = EmxBackend.supports_device
