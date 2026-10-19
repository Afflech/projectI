#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Run: ./scripts/install-docker-ubuntu.sh"
  exit 1
fi

if ! docker context inspect desktop-linux >/dev/null 2>&1; then
  echo "Docker Desktop context desktop-linux was not found."
  echo "Run: ./scripts/install-docker-desktop-ubuntu.sh"
  echo "Then open Docker Desktop and accept the terms."
  exit 1
fi

if ! docker --context desktop-linux info >/dev/null 2>&1; then
  echo "Docker Desktop is not reachable yet. Trying to start it..."
  systemctl --user start docker-desktop >/dev/null 2>&1 || true
fi

for _ in $(seq 1 30); do
  if docker --context desktop-linux info >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! docker --context desktop-linux info >/dev/null 2>&1; then
  echo "Docker Desktop is still not reachable."
  echo "Open Docker Desktop from the app menu, accept the terms, then rerun this script."
  exit 1
fi

mkdir -p backend/data
export DOCKER_UID="${DOCKER_UID:-$(id -u)}"
export DOCKER_GID="${DOCKER_GID:-$(id -g)}"

echo "Stopping this project in the system Docker Engine context to avoid port conflicts..."
docker --context default compose down --remove-orphans >/dev/null 2>&1 || true

for port in 5173 8000; do
  if ss -ltn "( sport = :$port )" | tail -n +2 | grep -q .; then
    echo "Port $port is still in use. Stop the process using it, then rerun this script."
    ss -ltnp "( sport = :$port )" || true
    exit 1
  fi
done

docker context use desktop-linux >/dev/null
docker compose up --build
