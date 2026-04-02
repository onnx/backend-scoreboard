# SPDX-License-Identifier: Apache-2.0

"""Tests for operator artifact generation in pytest reporting hooks."""

import importlib.util

from pathlib import Path


CONFTEST_PATH = Path(__file__).resolve().parent / "conftest.py"
SPEC = importlib.util.spec_from_file_location(
    "scoreboard_pytest_conftest", CONFTEST_PATH
)
CONFTEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONFTEST)


def test_prepare_ops_preserves_domain_and_adds_counts():
    """Serialize unique domain/op_type pairs with per-status test counts."""
    CONFTEST._suite_ops.clear()
    CONFTEST._test_proto_refs.clear()

    class Node:
        def __init__(self, domain, op_type):
            self.domain = domain
            self.op_type = op_type

    class Graph:
        def __init__(self, nodes):
            self.node = nodes

    class Model:
        def __init__(self, nodes):
            self.graph = Graph(nodes)

    CONFTEST._test_proto_refs.update(
        {
            "OnnxBackendNodeModelTest::test_add_cpu": [Model([Node("", "Add")])],
            "OnnxBackendNodeModelTest::test_ml_cpu": [
                Model([Node("", "Add"), Node("ai.onnx.ml", "ArrayFeatureExtractor")])
            ],
            "OnnxBackendNodeModelTest::test_ml_skip_cpu": [
                Model([Node("ai.onnx.ml", "ArrayFeatureExtractor")])
            ],
        }
    )

    report = {
        "passed": [
            "OnnxBackendNodeModelTest::test_add_cpu",
            "OnnxBackendNodeModelTest::test_ml_cpu",
        ],
        "failed": [],
        "skipped": ["OnnxBackendNodeModelTest::test_ml_skip_cpu"],
    }

    assert CONFTEST._prepare_ops(report) == [
        {
            "domain": "",
            "op_type": "Add",
            "total_tests": 2,
            "passed_tests": 2,
            "failed_tests": 0,
            "skipped_tests": 0,
        },
        {
            "domain": "ai.onnx.ml",
            "op_type": "ArrayFeatureExtractor",
            "total_tests": 2,
            "passed_tests": 1,
            "failed_tests": 0,
            "skipped_tests": 1,
        },
    ]


def test_normalize_record_name_removes_python_file_prefix():
    """Use the same normalized node id in report and ops mappings."""
    assert (
        CONFTEST._normalize_record_name(
            "test/test_backend.py::OnnxBackendNodeModelTest::test_add_cpu"
        )
        == "OnnxBackendNodeModelTest::test_add_cpu"
    )


def test_extract_ops_from_proto_ref_uses_mutable_onnx_mark_payload():
    """Read operator metadata from ONNX's mutable proto reference."""

    class Node:
        def __init__(self, domain, op_type):
            self.domain = domain
            self.op_type = op_type

    class Graph:
        def __init__(self, nodes):
            self.node = nodes

    class Model:
        def __init__(self, nodes):
            self.graph = Graph(nodes)

    proto_ref = [Model([Node("", "Add"), Node("ai.onnx.ml", "ArrayFeatureExtractor")])]

    assert CONFTEST._extract_ops_from_proto_ref(proto_ref) == {
        ("", "Add"),
        ("ai.onnx.ml", "ArrayFeatureExtractor"),
    }


def test_collection_uses_onnx_coverage_mark_proto_refs():
    """Store the ONNX coverage marker payload by normalized node id."""

    class Mark:
        def __init__(self, args):
            self.args = args

    class Item:
        def __init__(self, nodeid, mark):
            self.nodeid = nodeid
            self._mark = mark

        def get_closest_marker(self, name):
            if name == "onnx_coverage":
                return self._mark
            return None

    proto_ref = [object()]
    item = Item(
        "test/test_backend.py::OnnxBackendNodeModelTest::test_add_cpu",
        Mark((proto_ref, "NodeModel")),
    )

    CONFTEST._suite_ops.clear()
    CONFTEST._test_proto_refs.clear()
    CONFTEST.pytest_collection_modifyitems(None, None, [item])

    assert CONFTEST._test_proto_refs == {
        "OnnxBackendNodeModelTest::test_add_cpu": proto_ref
    }
