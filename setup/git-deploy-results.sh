#!/bin/bash

set -e  # Exit on error
set -x  # Command echo on

git remote set-url origin git@github.com:onnx/backend-scoreboard.git
git checkout master
git pull
git add results
git commit -m "Scoreboard results [skip ci]"
git push
