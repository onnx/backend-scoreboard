import onnx.backend.test
import unittest
import importlib
import sys


# Custom backend importer
def import_backend(backend_name):
    if backend_name.lower() == 'ngraph':
        return importlib.import_module('ngraph_onnx.core_importer.backend').NgraphBackend
    backend = importlib.import_module(backend_name)
    if not hasattr(backend, 'run_model'):
        raise ValueError('%s is not a valid ONNX backend', backend_name)
    return backend


# TODO: Handle backend name arg form command line
# Import custom backend
backend = import_backend(sys.argv[1])

# Set backend device name to be used
backend.backend_name = 'CPU'

# This is a pytest variable to load extra plugins
# Enable the ONNX compatibility report
pytest_plugins = 'onnx.backend.test.report'

# Import all test cases at global scope to make them visible to python.unittest
backend_test = onnx.backend.test.BackendTest(backend, __name__)

globals().update(backend_test.enable_report().test_cases)
globals().update(backend_test.test_cases)

if __name__ == '__main__':
    unittest.main()
