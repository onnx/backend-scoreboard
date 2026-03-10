#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


set -e  # Exit on error
set -x  # Command echo on

git fetch origin

# Switch to benchmark-results branch or create it as orphan on first run
if git ls-remote --heads origin benchmark-results | grep -q benchmark-results; then
  git checkout -B benchmark-results origin/benchmark-results
else
  git checkout --orphan benchmark-results
  git rm -rf --cached . 2>/dev/null || true
fi

git add results
if ! git diff --cached --quiet; then
  git commit -s -m "Scoreboard results [skip ci]"
  git push origin benchmark-results
else
  echo "No changes to commit"
fi
