import pytest
import test


def pytest_addoption(parser):
    parser.addoption('--onnx_backend',
                     choices=['ngraph_onnx.onnx_importer.backend',
                              'onnxruntime.backend.backend',
                              'onnxruntime.backend.backend',
                              'caffe2.python.onnx.backend'],
                     help='Select from available backends')


def pytest_configure(config):
    onnx_backend_module = config.getvalue('onnx_backend')
    test.ONNX_BACKEND_MODULE = onnx_backend_module
