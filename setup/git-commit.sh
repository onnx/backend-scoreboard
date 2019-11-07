#!/bin/bash

git pull origin master
git checkout master
git add results
git commit -m "Scoreboard results [ci skip]"
git push origin master
