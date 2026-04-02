# SPDX-License-Identifier: Apache-2.0

"""Merge benchmark trend histories centrally in the collect job."""

from __future__ import annotations

import csv
import json
import subprocess

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


REPORT_KEYS = ["passed", "failed", "skipped"]


def count_total_ops_from_ops_json(results_dir):
    """Count unique ops from ops.json for the current run."""
    ops = load_json_file(results_dir / "ops.json", [])
    if not isinstance(ops, list):
        return 0

    return len(
        {
            ((entry.get("domain") or ""), entry.get("op_type"))
            for entry in ops
            if isinstance(entry, dict) and entry.get("op_type")
        }
    )


def load_json_file(file_path, default):
    """Load JSON from a file and return a default value on failure."""
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except (IOError, json.decoder.JSONDecodeError):
        return default


def load_config(file_path):
    """Load the scoreboard configuration."""
    return load_json_file(file_path, {})


def load_json_from_git(base_ref, file_path):
    """Load JSON from a file stored in git at the specified ref."""
    relative_path = file_path.as_posix()
    command = ["git", "show", f"{base_ref}:{relative_path}"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    try:
        return json.loads(result.stdout)
    except json.decoder.JSONDecodeError:
        return []


def filter_packages(package_versions, backend_config):
    """Filter package versions down to the backend core packages."""
    core_packages = ["onnx", *backend_config.get("core_packages", [])]
    return [
        package for package in package_versions if package.get("name") in core_packages
    ]


def count_total_ops(results_dir):
    """Count unique ops from ops.json, falling back to nodes.csv."""
    total_ops = count_total_ops_from_ops_json(results_dir)
    if total_ops:
        return total_ops

    try:
        with open(results_dir / "nodes.csv", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return len({row.get("Op") for row in reader if row.get("Op") != "Summary"})
    except IOError:
        return 0


def build_summary(results_dir, backend_config):
    """Build a trend summary for the current benchmark artifact."""
    report = load_json_file(results_dir / "report.json", {})
    if not report:
        return None

    package_versions = load_json_file(results_dir / "pip-list.json", [])
    summary = {
        "date": report.get("date", datetime.now().strftime("%m/%d/%Y %H:%M:%S")),
        "versions": filter_packages(package_versions, backend_config),
        "total_ops": count_total_ops(results_dir),
    }
    for key in REPORT_KEYS:
        report_group = report.get(key, [])
        summary[key] = len(report_group) if isinstance(report_group, list) else 0
    return summary


def merge_trend(summary, trend):
    """Merge the current summary into the existing trend history."""
    if summary is None:
        return trend

    min_length = 2
    valid_length = len(trend) >= min_length and (
        len(summary.keys()) == len(trend[-1].keys())
    )
    equal_values = trend and all(
        summary.get(key) == trend[-1].get(key)
        for key in summary.keys()
        if key != "date"
    )
    if valid_length and equal_values:
        trend[-1] = summary
    else:
        trend.append(summary)
    return trend


def merge_backend_trend(base_ref, results_dir, backend_config):
    """Merge one backend results directory with the historical trend."""
    existing_trend = load_json_from_git(base_ref, results_dir / "trend.json")
    current_summary = build_summary(results_dir, backend_config)
    merged_trend = merge_trend(current_summary, existing_trend)

    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "trend.json", "w") as trend_file:
        json.dump(merged_trend, trend_file, sort_keys=True, indent=4)


def iter_backends(config):
    """Yield all backend configurations and their results directories."""
    for state in ("stable", "development"):
        for backend_config in config.get(state, {}).values():
            yield Path(backend_config.get("results_dir", "")), backend_config


def main():
    """Run the central trend merge for all configured backends."""
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        default="./setup/config.json",
        help="Path to the scoreboard config file",
        type=str,
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Git ref providing the previous trend history",
        type=str,
    )
    args = parser.parse_args()

    config = load_config(args.config)
    for results_dir, backend_config in iter_backends(config):
        if not str(results_dir):
            continue
        merge_backend_trend(args.base_ref, results_dir, backend_config)


if __name__ == "__main__":
    main()
