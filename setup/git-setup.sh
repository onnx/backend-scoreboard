#!/bin/bash

# SPDX-License-Identifier: Apache-2.0


set -e  # Exit on error
set -x  # Command echo on

git config --global user.name "GitHub Action"
git config --global user.email "action@github.com"

git fetch origin main
git checkout main
