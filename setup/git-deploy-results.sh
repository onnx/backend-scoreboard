#!/bin/bash

set -e  # Exit on error
set -x  # Command echo on

git pull origin master
git add results
git commit -m "Scoreboard results [skip ci]"
git remote set-url --push origin git@github.com:onnx/backend-scoreboard.git
git pull origin master
git push origin HEAD:master
