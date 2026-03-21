# SPDX-License-Identifier: Apache-2.0

"""ONNX backend wrapper for onnx2c (ONNX to C code generator)."""

import os
import re
import shutil
import subprocess
import tempfile

import numpy as np
from onnx import TensorProto, shape_inference
from onnx.backend.base import Backend, BackendRep
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt


def _c_name(name):
    """Convert ONNX tensor name to valid C identifier (matching onnx2c's naming)."""
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if name and name[0].isdigit():
        name = "_" + name
    return name


_ONNX_TO_C_TYPE = {
    TensorProto.FLOAT: "float",
    TensorProto.DOUBLE: "double",
    TensorProto.INT8: "int8_t",
    TensorProto.INT16: "int16_t",
    TensorProto.INT32: "int32_t",
    TensorProto.INT64: "int64_t",
    TensorProto.UINT8: "uint8_t",
    TensorProto.UINT16: "uint16_t",
    TensorProto.UINT32: "uint32_t",
    TensorProto.UINT64: "uint64_t",
    TensorProto.BOOL: "bool",
}

_ONNX_TO_NUMPY = {
    TensorProto.FLOAT: np.float32,
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


def _parse_tensor_info(value_info):
    """Return (c_name, c_type, numpy_dtype, shape) or None if unsupported."""
    t = value_info.type.tensor_type
    elem_type = t.elem_type
    c_type = _ONNX_TO_C_TYPE.get(elem_type)
    np_dtype = _ONNX_TO_NUMPY.get(elem_type)
    if c_type is None or np_dtype is None:
        return None

    shape = []
    if t.HasField("shape"):
        for dim in t.shape.dim:
            if dim.HasField("dim_value") and dim.dim_value > 0:
                shape.append(dim.dim_value)
            else:
                # Dynamic or unknown dimension — not supported by onnx2c
                return None
    else:
        return None

    return _c_name(value_info.name), c_type, np_dtype, shape


def _generate_harness(inputs_info, outputs_info):
    """Return C harness source that feeds inputs, calls entry(), writes outputs."""
    lines = [
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <stdint.h>",
        "#include <stdbool.h>",
        "",
    ]

    # extern declarations for input/output tensors (defined in generated model.c)
    for c_nm, c_type, _, shape in inputs_info:
        n = 1
        for d in shape:
            n *= d
        lines.append(f"extern {c_type} {c_nm}[{n}];")

    for c_nm, c_type, _, shape in outputs_info:
        n = 1
        for d in shape:
            n *= d
        lines.append(f"extern {c_type} {c_nm}[{n}];")

    lines += ["", "void entry(void);", "", "int main(int argc, char** argv) {"]
    lines.append("    FILE* f;")
    lines.append("")

    # Read inputs from files passed as argv[1..n_inputs]
    for i, (c_nm, c_type, _, shape) in enumerate(inputs_info):
        n = 1
        for d in shape:
            n *= d
        lines.append(f"    f = fopen(argv[{i + 1}], \"rb\");")
        lines.append(
            f"    if (!f) {{ fprintf(stderr, \"Cannot open input {i}\\n\"); return 1; }}"
        )
        lines.append(f"    fread({c_nm}, sizeof({c_type}), {n}, f);")
        lines.append("    fclose(f);")

    lines += ["", "    entry();", ""]

    # Write outputs to files passed as argv[n_inputs+1..n_inputs+n_outputs]
    n_in = len(inputs_info)
    for i, (c_nm, c_type, _, shape) in enumerate(outputs_info):
        n = 1
        for d in shape:
            n *= d
        lines.append(f"    f = fopen(argv[{n_in + i + 1}], \"wb\");")
        lines.append(
            f"    if (!f) {{ fprintf(stderr, \"Cannot open output {i}\\n\"); return 1; }}"
        )
        lines.append(f"    fwrite({c_nm}, sizeof({c_type}), {n}, f);")
        lines.append("    fclose(f);")

    lines += ["", "    return 0;", "}"]
    return "\n".join(lines)


class Onnx2cBackendRep(BackendRep):
    """Holds a compiled onnx2c binary and runs it for each inference call."""

    def __init__(self, binary_path, workdir, inputs_info, outputs_info):
        self._binary = binary_path
        self._workdir = workdir
        # Store only dtype and shape needed at run time
        self._input_dtypes = [np_dtype for _, _, np_dtype, _ in inputs_info]
        self._output_info = [(np_dtype, shape) for _, _, np_dtype, shape in outputs_info]

    def __del__(self):
        if self._workdir and os.path.isdir(self._workdir):
            shutil.rmtree(self._workdir, ignore_errors=True)

    def run(self, inputs, **kwargs):
        run_dir = tempfile.mkdtemp()
        try:
            # Write each input as raw binary with the expected dtype
            input_files = []
            for i, (inp, dtype) in enumerate(zip(inputs, self._input_dtypes)):
                path = os.path.join(run_dir, f"input_{i}.bin")
                np.asarray(inp, dtype=dtype).flatten().tofile(path)
                input_files.append(path)

            output_files = []
            for i in range(len(self._output_info)):
                path = os.path.join(run_dir, f"output_{i}.bin")
                output_files.append(path)

            result = subprocess.run(
                [self._binary] + input_files + output_files,
                capture_output=True,
                timeout=60,
            )
            if result.returncode != 0:
                raise BackendIsNotSupposedToImplementIt(
                    f"onnx2c binary failed: {result.stderr.decode()}"
                )

            outputs = []
            for path, (dtype, shape) in zip(output_files, self._output_info):
                arr = np.fromfile(path, dtype=dtype).reshape(shape)
                outputs.append(arr)
            return outputs
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)


class Onnx2cBackend(Backend):
    """ONNX backend that compiles models to native code via onnx2c."""

    @classmethod
    def is_compatible(cls, model, device="CPU", **kwargs):
        return True

    @classmethod
    def prepare(cls, model, device="CPU", **kwargs):
        # Run ONNX shape inference so output shapes are concrete where possible
        try:
            model = shape_inference.infer_shapes(model)
        except Exception:
            pass

        initializer_names = {init.name for init in model.graph.initializer}

        # Parse inputs (exclude initializers / weights)
        inputs_info = []
        for vi in model.graph.input:
            if vi.name in initializer_names:
                continue
            info = _parse_tensor_info(vi)
            if info is None:
                raise BackendIsNotSupposedToImplementIt(
                    f"Input '{vi.name}' has unsupported type or dynamic shape"
                )
            inputs_info.append(info)

        # Parse outputs
        outputs_info = []
        for vi in model.graph.output:
            info = _parse_tensor_info(vi)
            if info is None:
                raise BackendIsNotSupposedToImplementIt(
                    f"Output '{vi.name}' has unsupported type or dynamic shape"
                )
            outputs_info.append(info)

        workdir = tempfile.mkdtemp()
        try:
            # Serialize model
            model_path = os.path.join(workdir, "model.onnx")
            with open(model_path, "wb") as f:
                f.write(model.SerializeToString())

            # Generate C code with onnx2c
            result = subprocess.run(
                ["onnx2c", model_path], capture_output=True, timeout=120
            )
            if result.returncode != 0:
                raise BackendIsNotSupposedToImplementIt(
                    f"onnx2c failed: {result.stderr.decode()}"
                )
            model_c_path = os.path.join(workdir, "model.c")
            with open(model_c_path, "wb") as f:
                f.write(result.stdout)

            # Write harness
            harness_path = os.path.join(workdir, "harness.c")
            with open(harness_path, "w") as f:
                f.write(_generate_harness(inputs_info, outputs_info))

            # Compile
            binary_path = os.path.join(workdir, "model_exec")
            result = subprocess.run(
                ["gcc", "-O2", "-o", binary_path, harness_path, model_c_path, "-lm"],
                capture_output=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise BackendIsNotSupposedToImplementIt(
                    f"Compilation failed: {result.stderr.decode()}"
                )

            return Onnx2cBackendRep(binary_path, workdir, inputs_info, outputs_info)

        except BackendIsNotSupposedToImplementIt:
            shutil.rmtree(workdir, ignore_errors=True)
            raise
        except Exception as e:
            shutil.rmtree(workdir, ignore_errors=True)
            raise BackendIsNotSupposedToImplementIt(str(e)) from e

    @classmethod
    def run_model(cls, model, inputs, device="CPU", **kwargs):
        return cls.prepare(model, device, **kwargs).run(inputs)

    @classmethod
    def supports_device(cls, device):
        return device == "CPU"


prepare = Onnx2cBackend.prepare
run_model = Onnx2cBackend.run_model
supports_device = Onnx2cBackend.supports_device
