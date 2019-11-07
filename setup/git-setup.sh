#!/bin/bash
git config --global user.email "scoreboard@pipeline.com"
git config --global user.name "scoreboard-pipeline"

git pull origin master
git checkout master
