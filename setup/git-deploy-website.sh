#!/bin/bash

set -e  # Exit on error
set -x  # Command echo on

git remote set-url origin git@github.com:onnx/backend-scoreboard.git
git checkout master
git pull
git add docs
git commit -m "Upadate website [skip ci]" || true  # Do not fail if nothing to commit
git push
