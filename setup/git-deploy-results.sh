#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


set -e  # Exit on error
set -x  # Command echo on

git checkout master
git pull
git add results
git commit -m "Scoreboard results [skip ci]"
git push
