#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


set -e  # Exit on error
set -x  # Command echo on

git checkout main
git pull
git add docs
if ! git diff --cached --quiet; then
  git commit -s -m "Update website [skip ci]"
  git push
else
  echo "No changes to commit"
fi
