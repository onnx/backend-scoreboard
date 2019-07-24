import onnx.backend.test
import unittest

# Import backend
import caffe2.python.onnx.backend as backend

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
