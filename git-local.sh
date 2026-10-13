#!/usr/bin/env sh
set -eu

git --git-dir=.gitlocal --work-tree=. "$@"
