# SPDX-License-Identifier: Apache-2.0

"""Tests for central trend merging."""

import json

from pathlib import Path

from scripts.merge_trends import build_summary, merge_trend


def test_build_summary_uses_report_and_core_packages(tmp_path):
    """Build summary from report and pip list artifacts."""
    results_dir = Path(tmp_path)
    report = {
        "date": "03/25/2026 00:50:48",
        "failed": ["f1", "f2"],
        "passed": ["p1", "p2", "p3"],
        "skipped": ["s1"],
    }
    package_versions = [
        {"name": "onnx", "version": "1.20.1"},
        {"name": "onnxruntime", "version": "1.22.0"},
        {"name": "numpy", "version": "2.0.0"},
    ]
    nodes_csv = "Op,None\nAdd,Passed!\nMul,Failed!\nMul,Passed!\n"
    (results_dir / "report.json").write_text(json.dumps(report))
    (results_dir / "pip-list.json").write_text(json.dumps(package_versions))
    (results_dir / "nodes.csv").write_text(nodes_csv)

    summary = build_summary(results_dir, {"core_packages": ["onnxruntime"]})

    assert summary == {
        "date": "03/25/2026 00:50:48",
        "failed": 2,
        "passed": 3,
        "skipped": 1,
        "total_ops": 2,
        "versions": [
            {"name": "onnx", "version": "1.20.1"},
            {"name": "onnxruntime", "version": "1.22.0"},
        ],
    }


def test_merge_trend_appends_new_summary():
    """Append a changed summary to the existing trend."""
    previous_trend = [
        {
            "date": "03/24/2026 00:50:48",
            "failed": 1,
            "passed": 3,
            "skipped": 0,
            "total_ops": 10,
            "versions": [{"name": "onnx", "version": "1.20.1"}],
        }
    ]
    summary = {
        "date": "03/25/2026 00:50:48",
        "failed": 2,
        "passed": 3,
        "skipped": 0,
        "total_ops": 10,
        "versions": [{"name": "onnx", "version": "1.20.1"}],
    }

    merged = merge_trend(summary, previous_trend)

    assert len(merged) == 2
    assert merged[-1] == summary


def test_merge_trend_replaces_last_identical_summary():
    """Retain the existing identical-summary replacement behavior."""
    previous_trend = [
        {
            "date": "03/23/2026 00:50:48",
            "failed": 1,
            "passed": 3,
            "skipped": 0,
            "total_ops": 10,
            "versions": [{"name": "onnx", "version": "1.20.1"}],
        },
        {
            "date": "03/24/2026 00:50:48",
            "failed": 1,
            "passed": 3,
            "skipped": 0,
            "total_ops": 10,
            "versions": [{"name": "onnx", "version": "1.20.1"}],
        },
    ]
    summary = {
        "date": "03/25/2026 00:50:48",
        "failed": 1,
        "passed": 3,
        "skipped": 0,
        "total_ops": 10,
        "versions": [{"name": "onnx", "version": "1.20.1"}],
    }

    merged = merge_trend(summary, previous_trend)

    assert len(merged) == 2
    assert merged[-1]["date"] == "03/25/2026 00:50:48"
