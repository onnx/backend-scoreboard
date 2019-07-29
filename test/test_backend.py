import importlib
import sys
import test
import unittest

import onnx.backend.test


# Custom backend importer
def import_backend(onnx_backend_module):
    backend = importlib.import_module(onnx_backend_module)
    if not hasattr(backend, 'run_model') and not hasattr(backend, 'run'):
        raise ValueError('%s is not a valid ONNX backend', onnx_backend_module)
    return backend


# Import custom backend
backend = import_backend(test.ONNX_BACKEND_MODULE)

# Set backend device name to be used
backend.backend_name = 'CPU'

# This is a pytest variable to load extra plugins
# Enable the ONNX compatibility report
pytest_plugins = 'onnx.backend.test.report'

# Import all test cases at global scope to make them visible to python.unittest
backend_test = onnx.backend.test.BackendTest(backend, __name__)
globals().update(backend_test.enable_report().test_cases)


if __name__ == '__main__':
    unittest.main()
