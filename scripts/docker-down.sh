#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1 && getent group docker | grep -q "\b${USER}\b"; then
  exec sg docker -c "cd '$(pwd)' && ./scripts/docker-down.sh"
fi

docker compose down
