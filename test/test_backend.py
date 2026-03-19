# SPDX-License-Identifier: Apache-2.0

"""ONNX backend test initialization."""

import functools
import importlib
import os
import unittest

import onnx.backend.test
import onnx.backend.test.runner as onnx_test_runner


def import_backend(onnx_backend_module):
    """Import ONNX backend module.

    :param onnx_backend_module: ONNX backend module to import.
    :type onnx_backend_module: str
    :raises ValueError: Not a valid ONNX backend.
    :return: The ONNX backend module.
    :rtype: class 'module'
    """
    backend = importlib.import_module(onnx_backend_module)
    if not hasattr(backend, "run_model") and not hasattr(backend, "run"):
        raise ValueError("%s is not a valid ONNX backend", onnx_backend_module)
    return backend


def _device_test_name(test_name, device):
    return f"{test_name}_{device.lower()}"


def _guard_duplicate_test(test_items, category, device_test_name):
    if device_test_name in test_items[category]:
        raise ValueError(
            f'Duplicated test name "{device_test_name}" in category "{category}"'
        )


def _wrap_device_test(self, test_func, device, device_test_name, kwargs):
    @unittest.skipIf(
        not self.backend.supports_device(device),
        f"Backend doesn't support device {device}",
    )
    @functools.wraps(test_func)
    def device_test_func(*args, **device_test_kwarg):
        try:
            merged_kwargs = {**kwargs, **device_test_kwarg}
            return test_func(*args, device, **merged_kwargs)
        except onnx_test_runner.BackendIsNotSupposedToImplementIt as err:
            # Surface backend opt-outs as real pytest skips so they end up
            # in report.json/trend.json under "skipped" instead of "passed".
            raise unittest.SkipTest(
                f"{device_test_name} skipped by backend code: {err}"
            ) from err

    return device_test_func


def _add_test_hardened(
    self,
    category,
    test_name,
    test_func,
    report_item,
    devices=("CPU", "CUDA"),
    **kwargs,
):
    if not test_name.startswith("test_"):
        raise ValueError(f"Test name must start with test_: {test_name}")

    for device in devices:
        device_test_name = _device_test_name(test_name, device)
        _guard_duplicate_test(self._test_items, category, device_test_name)
        device_test_func = _wrap_device_test(
            self, test_func, device, device_test_name, kwargs
        )
        self._test_items[category][device_test_name] = onnx_test_runner.TestItem(
            device_test_func, report_item
        )


def harden_backend_test_skips():
    """Treat backend opt-out exceptions as explicit skips in pytest stats."""
    if getattr(onnx_test_runner.Runner, "_scoreboard_hardened", False):
        return

    onnx_test_runner.Runner._add_test = _add_test_hardened
    onnx_test_runner.Runner._scoreboard_hardened = True


# Import custom backend
backend = import_backend(os.getenv("ONNX_BACKEND_MODULE"))

# Set backend device name to be used
backend.backend_name = "CPU"

harden_backend_test_skips()

# This is a pytest variable to load extra plugins
# Enable the ONNX compatibility report
pytest_plugins = "onnx.backend.test.report"

# Import all test cases at global scope to make them visible to python.unittest
backend_test = onnx.backend.test.BackendTest(backend, __name__)
globals().update(backend_test.enable_report().test_cases)


if __name__ == "__main__":
    unittest.main()
