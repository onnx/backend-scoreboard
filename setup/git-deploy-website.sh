#!/bin/bash

set -e  # Exit on error
set -x  # Command echo on

git remote set-url origin git@github.com:onnx/backend-scoreboard.git
git checkout master
git pull
git add docs
git commit -m "Upadate website [skip ci]" || true  # Not failed if nothing to commit
git push
