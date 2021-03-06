# SPDX-License-Identifier: Apache-2.0

"""Static page generator based on jinja2 templates API.

Jinja2 docs: https://jinja.palletsprojects.com/en/2.10.x/api/
"""

import csv
import json
import os
import shutil

from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape


class ScoreboardError(Exception):
    """Base class for exceptions in this module."""

    pass


def load_trend(file_dir, file_name="trend.json"):
    """Load and return trend list from JSON file.

    Return list of summaries loaded from tests trend JSON file.
    If the file is broken, empty or not found then create and return a new dummy trend.
    Trend is a list of report summaries per date.
    This enables tracking of the number of failed and passed tests.
    Trend example:
    [
        {
            "date": "08/06/2019 09:37:45",
            "failed": 61,
            "passed": 497,
            "skipped": 0,
            "versions": [
                {
                    "name": "onnx",
                    "version": "1.5.0"
                }
            ]
        },
        {
            "date": "08/08/2019 08:34:18",
            "failed": 51,
            "passed": 507,
            "skipped": 0,
            "versions": [
                {
                    "name": "onnx",
                    "version": "1.6.0"
                }
            ]
        }
    ]
    :param file_dir: Path to the dir with trend JSON file.
    :type path: str
    :param file_name: Name of trend file.
    :type path: str
    :return: List of summaries.
    :rtype: list
    """
    dummy_trend = [
        {
            "date": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            "failed": 0,
            "passed": 0,
            "skipped": 0,
        }
    ]

    try:
        with open(os.path.join(file_dir, file_name), "r") as trend_file:
            trend = json.load(trend_file)
        if not trend:
            raise IndexError
    except (IndexError, IOError, json.decoder.JSONDecodeError):
        trend = dummy_trend
    return trend


def mark_coverage(percentage):
    """Return a mark from A to F based on the passed tests percentage.

    :param percentage: Percentage of passed unit tests.
    :type percentage: float
    :return: Mark from A to F.
    :rtype: str
    """
    mark_table = {
        "A": (90, 101),
        "B": (80, 90),
        "C": (70, 80),
        "D": (60, 70),
        "F": (0, 59),
    }
    for mark, mark_range in mark_table.items():
        if int(percentage) in range(*mark_range):
            return mark


def get_coverage_percentage(trend):
    """Create and return a dict with passed and failed tests percentage.

    :param trend: Trend is a list of report summaries per date.
    :type trend: list
    :return: Dictionary with passed and failed tests percentage.
    :rtype: dict
    """
    try:
        latest_result = trend[-1]
    except IndexError:
        trend = [
            {
                "date": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                "failed": 0,
                "passed": 0,
                "skipped": 0,
            }
        ]
        latest_result = trend[-1]

    coverage = {}
    try:
        coverage["total"] = (
            latest_result.get("failed", 0)
            + latest_result.get("passed", 0)
            + latest_result.get("skipped", 0)
        )
        coverage["passed"] = (
            latest_result.get("passed", 0) / coverage.get("total", 0) * 100
        )
        coverage["failed"] = (
            latest_result.get("failed", 0) / coverage.get("total", 0) * 100
        )
        coverage["skipped"] = (
            latest_result.get("skipped", 0) / coverage.get("total", 0) * 100
        )
    except ZeroDivisionError:
        coverage["passed"] = 0
        coverage["failed"] = 0
        coverage["skipped"] = 0

    coverage["mark"] = mark_coverage(coverage["passed"])
    return coverage


def load_ops_csv(file_dir, file_name="nodes.csv"):
    """Load operators list and their coverage from the specified CSV file.

    This CSV file should be generated by onnx.backend.test.report at the end of testing.
    It contains rows with operator name and "passed" or "failed" status.

    :param file_dir: Path to the dir with the operators coverage CSV file.
    :type file_dir: str
    :param file_name: Name of the operators coverage file, defaults to "nodes.csv".
    :type file_name: str, optional
    :return: Dict with operator name as a key and status as a value.
    :rtype: OrderedDict
    """
    ops_table = OrderedDict()
    try:
        with open(os.path.join(file_dir, file_name), newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                ops_table[row["Op"]] = row.get("None", "").replace("!", "").lower()
    except IOError:
        pass  # Return empty dict
    return ops_table


def load_report(file_dir, file_name="report.json"):
    """Load unit tests report from the specified JSON file.

    Report is a dictionary that contains test status ("failed"/"passed"/"skipped")
    as a key and list of test names as a value.

    :param file_dir: Path to the dir with report JSON file.
    :type file_dir: str
    :param file_name: Name of the report JSON file, defaults to "report.json".
    :type file_name: str, optional
    :return: Swapped report that contains test name as a key and status as a value.
    :rtype: OrderedDict
    """
    dummy_report = {"failed": [], "passed": [], "skipped": []}
    try:
        with open(os.path.join(file_dir, file_name), "r") as report_file:
            report = json.load(report_file)
            report.pop("date", None)
    except (IOError, json.decoder.JSONDecodeError):
        report = dummy_report

    # Swap value with keys to make displaying data easier
    swapped_report = OrderedDict()
    for status, test_names in report.items():
        for test in test_names:
            swapped_report[test] = status

    swapped_report = OrderedDict(
        sorted(swapped_report.items(), key=lambda item: item[0])
    )
    return swapped_report


def load_config(file_path="./setup/config.json"):
    """Load scoreboard configuration file.

    Configuration file contains a list of backends included in the scoreboard.
    This is a place for information about results path or core package names.
    Each new runtime has to be added to this file. (More info in README.md)

    :param file_path: Path to the config file, defaults to "./setup/config.json"
    :type file_path: str
    :raises ScoreboardError: Raise ScoreboardError if config file can't be loaded.
    :return: Dictionary with the scoreboard configuration.
    :rtype: dict
    """
    file_path = os.path.abspath(file_path)
    try:
        with open(file_path, "r") as config_file:
            config = json.load(config_file)
    except (IOError, json.decoder.JSONDecodeError) as err:
        raise ScoreboardError("Can't load the scoreboard config file!", err)
    return config


def prepare_database(config, state="stable"):
    """Prepare all backends data to be stored and passed to the templates.

    Database is a dictionary that contains backend id as a key and
    all results data as a value.

    :param config: Dictionary with the scoreboard config (documented in README.md).
    :type config: dict
    :param state: Use "stable" or "dev" to choose runtimes version, defaults to "stable"
    :type state: str, optional
    :return: Dictionary with results data for the listed in the config backends.
    :rtype: OrderedDict
    """
    repo_url = config.get("repo_url", "")
    config = config.get(state, {})
    database = OrderedDict()

    for backend_id, backend_config in config.items():
        results_dir = backend_config.get("results_dir", "")
        dockerfile_link = backend_config.get("dockerfile_link", "")
        name = backend_config.get("name", backend_id)
        trend = load_trend(results_dir)
        coverage = get_coverage_percentage(trend)
        ops = load_ops_csv(results_dir)
        report = load_report(results_dir)

        database[backend_id] = {
            "name": name,
            "trend": trend,
            "coverage": coverage,
            "ops": ops,
            "report": report,
            "dockerfile_link": repo_url + dockerfile_link,
        }

    database = sort_by_score(database)
    return database


def generate_page(template, output_dir, name, **template_args):
    """Generate HTML page based on the passed template.

    :param template: Jinja2 HTML template.
    :type template: jinja2.Template
    :param output_dir: Directory to save generated HTML page.
    :type output_dir: str
    :param name: Name of the output file.
    :type name: str
    :param **template_args: Variables that should be visible in the template.
    """
    page = template.render(template_args)

    # Save HTML page to file
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, name), "w+") as f:
        f.write(page)


def generate_pages(template, database, suffix):
    """Generate HTML page for each backend in the specified database.

    :param template: Jinja2 HTML template, generated from jinja2.Environment.
    :type template: jinja2.Template
    :param database: Dictionary with results data for backends listed in the config.
    :type database: dict
    :param suffix: File name suffix for the output, e.g. "details_stable.html".
    :type suffix: str
    """
    for backend, backend_data in database.items():
        output_name = "{name}_{suffix}".format(name=backend, suffix=suffix)
        generate_page(
            template,
            deploy_paths.get("subpages", "./"),
            output_name,
            backend_data=backend_data,
        )


def sort_by_score(database):
    """Sort database by backend score (percentage of passed tests) in descending order.

    :param database: Dictionary with results data for backends listed in the config.
    :type database: dict
    :return: Sorted database.
    :rtype: OrderedDict
    """
    database = OrderedDict(
        sorted(
            database.items(),
            key=lambda item: item[1]["coverage"]["passed"],
            reverse=True,
        )
    )
    return database


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        dest="config",
        help="Load configuration from the specified json file",
        default="./setup/config.json",
        type=str,
    )
    args = parser.parse_args()

    # Load configuration from file
    config = load_config(args.config)
    deploy_paths = config.get("deploy_paths")

    # Prepare data for templates
    database_stable = prepare_database(config, state="stable")
    database_dev = prepare_database(config, state="development")

    # Website
    # Create Jinja2 templates environment
    env = Environment(
        loader=PackageLoader("templates-module", "templates"),
        autoescape=select_autoescape(["html"]),
    )

    # Create index.html file
    template = env.get_template("index.html")
    generate_page(
        template,
        deploy_paths.get("index", "./"),
        "index.html",
        database=database_stable,
    )

    # Create dev subpage
    template = env.get_template("index.html")
    generate_page(
        template,
        deploy_paths.get("subpages", "./"),
        "index_dev.html",
        database=database_dev,
        development_versions_selected=True,
    )

    # Create backends_comparison subpage
    template = env.get_template("backends_comparison.html")
    generate_page(
        template,
        deploy_paths.get("subpages", "./"),
        "backends_comparison_stable.html",
        database=database_stable,
    )

    # Create details page for each backend
    template = env.get_template("details.html")
    generate_pages(template, database_stable, "details_stable.html")
    generate_pages(template, database_dev, "details_dev.html")

    # Copy resources to deploy dir
    # shutil.copytree function raises error if destination path exists
    resources_path = os.path.abspath("./website-generator/resources")
    deploy_resources_path = os.path.abspath(
        deploy_paths.get("resources", "./docs/resources")
    )
    if os.path.exists(deploy_resources_path):
        shutil.rmtree(deploy_resources_path)
    shutil.copytree(resources_path, deploy_resources_path)
