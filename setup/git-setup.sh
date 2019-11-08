#!/bin/bash
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

git config --global user.email "onnx_scoreboard_bot@azure"
git config --global user.name "ONNX Scoreboard Bot @ Azure Pipelines"

git pull origin master
git checkout master
