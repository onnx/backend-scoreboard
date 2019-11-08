#!/bin/bash

git pull origin master
git add docs
git commit --allow-empty -m "Upadate website [skip ci]"
git remote set-url --push origin git@github.com:onnx/backend-scoreboard.git
git pull origin master
git push origin HEAD:master
