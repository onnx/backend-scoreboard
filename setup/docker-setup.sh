#!/bin/bash
cd ~
pip list --format=json > ${RESULTS_DIR}/pip-list.json
