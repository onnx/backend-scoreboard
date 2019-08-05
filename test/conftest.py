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
    # Date and time of report
    date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    # Keys for values to save in report (matched with terminalreporter.stats)
    report_keys = ['passed', 'failed', 'skipped']

    # Collect results report
    report = dict()
    report['date'] = date
    for key in report_keys:
        stats_group = terminalreporter.stats.get(key, [])
        if isinstance(stats_group, list):
            report[key] = []
            for record in stats_group:
                if hasattr(record, 'nodeid'):
                    # Remove file name from test id
                    split_id = record.nodeid.split('::')
                    clear_id = filter(lambda x: '.py' not in x, split_id)
                    record_name = '::'.join(clear_id)
                    report[key].append(record_name)
        report[key].sort()

    # Set directory for results
    results_dir = os.environ.get('RESULTS_DIR', os.getcwd())

    # Update file with test summary
    with open(os.path.join(results_dir, 'report.json'), 'w') as report_file:
        json.dump(report, report_file, sort_keys=True)

    # Make summary of tests
    summary = dict()
    summary['date'] = date
    for key in report_keys:
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
           for key in summary.keys() if key != 'date'):
        trend.append(summary)
    else:
        trend[-1] = summary

    # Save trend data to the file
    with open(os.path.join(results_dir, 'trend.json'), 'w') as trend_file:
        json.dump(trend, trend_file, sort_keys=True)
