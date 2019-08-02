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
    failed_report = terminalreporter.stats.get('failed', [])
    passed_report = terminalreporter.stats.get('passed', [])
    skipped_report = terminalreporter.stats.get('skipped', [])

    report = dict()
    report['failed_list'] = [test.nodeid for test in failed_report]
    report['passed_list'] = [test.nodeid for test in passed_report]
    report['skipped_list'] = [test.nodeid for test in skipped_report]
    report['date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    # Set directory for results
    results_dir = os.environ.get('RESULTS_DIR', os.getcwd())

    # Update file with test summary
    with open(os.path.join(results_dir, 'report.json'), 'w') as report_file:
        json.dump(report, report_file)

    # Count amount of failed, passed and skipped tests
    summary = dict()
    summary['failed_sum'] = len(report.get('failed_list'))
    summary['passed_sum'] = len(report.get('passed_list'))
    summary['skipped_sum'] = len(report.get('skipped_list'))
    summary['date'] = report.get('date')

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
    if len(trend) < 2 or \
       trend[-1].get('failed_sum') != summary.get('failed_sum') or \
       trend[-1].get('passed_sum') != summary.get('passed_sum') or \
       trend[-1].get('skipped_sum') != summary.get('skipped_sum'):
        trend.append(summary)
    else:
        trend[-1] = summary

    # Save trend data to the file
    with open(os.path.join(results_dir, 'trend.json'), 'w') as trend_file:
        json.dump(trend, trend_file)
