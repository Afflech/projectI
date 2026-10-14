#!/usr/bin/env bash
set -euo pipefail

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required to install Docker."
  exit 1
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo "Docker and Docker Compose are already installed."
  docker --version
  docker compose version
  exit 0
fi

. /etc/os-release
if [ "${ID:-}" != "ubuntu" ]; then
  echo "This installer is intended for Ubuntu. Detected: ${PRETTY_NAME:-unknown}"
  exit 1
fi

sudo install -m 0755 -d /etc/apt/keyrings
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' \
  "$(dpkg --print-architecture)" \
  "${VERSION_CODENAME}" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker

if ! groups "$USER" | grep -q '\bdocker\b'; then
  sudo usermod -aG docker "$USER"
  echo "Added $USER to the docker group. Log out and back in before running Docker without sudo."
fi

docker --version || sudo docker --version
docker compose version || sudo docker compose version
