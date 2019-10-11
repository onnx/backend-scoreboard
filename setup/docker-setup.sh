#!/bin/bash

# This script contains all commands which need to be executed
# before running the tests.

pip list --format=json > ${RESULTS_DIR}/pip-list.json
