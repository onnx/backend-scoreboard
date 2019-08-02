import json
import os
import pytest
import test

from datetime import datetime


def pytest_addoption(parser):
    parser.addoption('--onnx_backend',
                     choices=['ngraph_onnx.onnx_importer.backend',
                              'onnxruntime.backend.backend',
                              'onnx_tf.backend',
                              'caffe2.python.onnx.backend'],
                     help='Select from available backends')


def pytest_configure(config):
    onnx_backend_module = config.getvalue('onnx_backend')
    test.ONNX_BACKEND_MODULE = onnx_backend_module


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    # Collect results report
    report = dict()
    report['date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    for key in terminalreporter.stats.keys():
        stats_group = terminalreporter.stats[key]
        if isinstance(stats_group, list):
            report[key] = []
            for record in stats_group:
                if hasattr(record, 'nodeid'):
                    splited_record_name = record.nodeid.split('::')
                    try:
                        record_name = '::'.join(splited_record_name[-2::])
                    except IndexError:
                        record_name = record.nodeid
                    report[key].append(record_name)

    # Set directory for results
    results_dir = os.environ.get('RESULTS_DIR', os.getcwd())

    # Update file with test summary
    with open(os.path.join(results_dir, 'report.json'), 'w') as report_file:
        json.dump(report, report_file)

    # Make summary of tests
    summary = dict()
    for key in report.keys():
        if isinstance(report[key], list):
            summary[key] = len(report[key])

    # Open file with test trends
    # If file is broken, empty or not found create new trend list
    try:
        with open(os.path.join(results_dir, 'trend.json'), 'r') as trend_file:
            trend = json.load(trend_file)
    except (IOError, json.decoder.JSONDecodeError):
        trend = []

    # Append result summary if trend has less than two results or
    # the last one result is different than current,
    # otherwise replace last summary
    if len(trend) < 2 or len(summary.keys()) != len(trend[-1].keys()) or \
       any(trend[-1].get(key) != summary.get(key)
           for key in summary.keys() if key != 'data'):
        trend.append(summary)
    else:
        trend[-1] = summary

    # Save trend data to the file
    with open(os.path.join(results_dir, 'trend.json'), 'w') as trend_file:
        json.dump(trend, trend_file)
