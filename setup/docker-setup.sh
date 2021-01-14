#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


# This script contains all commands which need to be executed
# before running the tests.

set -e  # Exit on error
set -x  # Command echo on

pip list --format=json > "${RESULTS_DIR}"/pip-list.json
