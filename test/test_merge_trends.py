# SPDX-License-Identifier: Apache-2.0

"""Tests for central trend merging."""

import json

from pathlib import Path

from scripts.merge_trends import (
    build_summary,
    count_total_ops,
    count_total_ops_from_ops_json,
    merge_trend,
)


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
    ops = [
        {"domain": "", "op_type": "Add"},
        {"domain": "ai.onnx.ml", "op_type": "ArrayFeatureExtractor"},
        {"domain": "", "op_type": "Add"},
    ]
    (results_dir / "report.json").write_text(json.dumps(report))
    (results_dir / "pip-list.json").write_text(json.dumps(package_versions))
    (results_dir / "ops.json").write_text(json.dumps(ops))

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


def test_count_total_ops_prefers_ops_json(tmp_path):
    """Use ops.json as the authoritative source when present."""
    results_dir = Path(tmp_path)
    ops = [
        {"domain": "", "op_type": "Add"},
        {"domain": "ai.onnx.ml", "op_type": "ArrayFeatureExtractor"},
        {"domain": "", "op_type": "Add"},
    ]
    (results_dir / "ops.json").write_text(json.dumps(ops))
    (results_dir / "nodes.csv").write_text("Op,None\nAdd,Passed!\nMul,Failed!\n")

    assert count_total_ops_from_ops_json(results_dir) == 2
    assert count_total_ops(results_dir) == 2


def test_count_total_ops_falls_back_to_nodes_csv_without_ops_json(tmp_path):
    """Keep supporting older artifacts that only have nodes.csv."""
    results_dir = Path(tmp_path)
    (results_dir / "nodes.csv").write_text(
        "Op,None\nAdd,Passed!\nMul,Failed!\nSummary,1/2 node tests passed\n"
    )

    assert count_total_ops_from_ops_json(results_dir) == 0
    assert count_total_ops(results_dir) == 2


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
