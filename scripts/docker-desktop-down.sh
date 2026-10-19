#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed."
  exit 1
fi

if ! docker context inspect desktop-linux >/dev/null 2>&1; then
  echo "Docker Desktop context desktop-linux was not found."
  exit 1
fi

docker --context desktop-linux compose down
