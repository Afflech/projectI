#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Run: ./scripts/install-docker-ubuntu.sh"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1 && getent group docker | grep -q "\b${USER}\b"; then
  exec sg docker -c "cd '$(pwd)' && DOCKER_UID='$(id -u)' DOCKER_GID='$(id -g)' ./scripts/docker-up.sh"
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is not available. Run: ./scripts/install-docker-ubuntu.sh"
  exit 1
fi

mkdir -p backend/data
export DOCKER_UID="${DOCKER_UID:-$(id -u)}"
export DOCKER_GID="${DOCKER_GID:-$(id -g)}"

docker compose up --build
