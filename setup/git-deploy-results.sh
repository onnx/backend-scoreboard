#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


set -e  # Exit on error
set -x  # Command echo on

git checkout master
git pull
git add results
if ! git diff --cached --quiet; then
  git commit -s -m "Scoreboard results [skip ci]"
  git push
else
  echo "No changes to commit"
fi
