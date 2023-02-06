#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


set -e  # Exit on error
set -x  # Command echo on

git checkout master
git pull
git add docs
git commit -m "Update website [skip ci]" || true  # Do not fail if nothing to commit
git push
