# SPDX-License-Identifier: Apache-2.0

"""Tests for website generator coverage calculations."""

import importlib.util

from pathlib import Path


GENERATOR_PATH = (
    Path(__file__).resolve().parent.parent / "website-generator" / "generator.py"
)
SPEC = importlib.util.spec_from_file_location("scoreboard_generator", GENERATOR_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def test_coverage_score_uses_test_pass_rate_even_with_total_ops():
    """Keep the overview score aligned with the trend's unit test percentage."""
    trend = [
        {
            "date": "04/01/2026 00:59:17",
            "passed": 482,
            "failed": 141,
            "skipped": 814,
            "total_ops": 194,
        }
    ]
    ops = {"Add": "passed", "Mul": "passed", "Sub": "failed"}

    coverage = GENERATOR.get_coverage_percentage(trend, ops)

    assert round(coverage["tests_passed"], 2) == 33.54
    assert round(coverage["passed"], 2) == 33.54
    assert coverage["passed_ops"] == 2
    assert coverage["total_ops"] == 194


def test_load_ops_csv_ignores_summary_row(tmp_path):
    """Ignore the synthetic Summary row in nodes.csv."""
    csv_content = "\n".join(
        [
            "Op,None",
            "Add,Passed!",
            "Mul,Failed!",
            "Summary,105/193 node tests passed",
        ]
    )
    (tmp_path / "nodes.csv").write_text(csv_content)

    ops = GENERATOR.load_ops_csv(tmp_path)

    assert list(ops.keys()) == ["Add", "Mul"]
    assert ops["Add"] == "passed"
    assert ops["Mul"] == "failed"


def test_load_ops_summary_reads_summary_row(tmp_path):
    """Expose the synthetic Summary row separately from operator coverage."""
    csv_content = "\n".join(
        [
            "Op,None",
            "Add,Passed!",
            "Summary,105/193 node tests passed",
        ]
    )
    (tmp_path / "nodes.csv").write_text(csv_content)

    summary = GENERATOR.load_ops_summary(tmp_path)

    assert summary == "105/193 node tests passed"
