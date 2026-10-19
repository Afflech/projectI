#!/usr/bin/env bash
set -euo pipefail

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required to install Docker Desktop."
  exit 1
fi

. /etc/os-release
if [ "${ID:-}" != "ubuntu" ]; then
  echo "This installer is intended for Ubuntu. Detected: ${PRETTY_NAME:-unknown}"
  exit 1
fi

arch="$(dpkg --print-architecture)"
if [ "$arch" != "amd64" ]; then
  echo "Docker Desktop Linux package in this script expects amd64. Detected: $arch"
  exit 1
fi

download_dir="${XDG_DOWNLOAD_DIR:-$HOME/Downloads}"
mkdir -p "$download_dir"
deb_path="$download_dir/docker-desktop-amd64.deb"

echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnome-terminal

echo "Downloading Docker Desktop package to $deb_path..."
curl -fL "https://desktop.docker.com/linux/main/amd64/docker-desktop-amd64.deb" -o "$deb_path"

if [ -n "${DOCKER_DESKTOP_DEB_SHA256:-}" ]; then
  echo "${DOCKER_DESKTOP_DEB_SHA256}  ${deb_path}" | sha256sum -c -
fi

echo "Installing Docker Desktop..."
sudo apt-get install -y "$deb_path"

if getent group kvm >/dev/null 2>&1; then
  sudo usermod -aG kvm "$USER"
fi

echo
echo "Docker Desktop is installed."
echo "Next steps:"
echo "1. Log out and back in so the kvm group membership is active."
echo "2. Open Docker Desktop from the app menu, or run:"
echo "   systemctl --user start docker-desktop"
echo "3. Accept the Docker Desktop terms in the UI."
echo
echo "Docker Desktop uses its own context named desktop-linux."
echo "Use 'docker context ls' to see current Docker targets."
