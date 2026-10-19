#!/usr/bin/env bash
set -euo pipefail

ok() {
  printf '[ok] %s\n' "$1"
}

warn() {
  printf '[warn] %s\n' "$1"
}

fail() {
  printf '[fail] %s\n' "$1"
}

if ! command -v docker >/dev/null 2>&1; then
  fail "Docker CLI is not installed."
  exit 1
fi
ok "Docker CLI found: $(docker --version)"

if docker context inspect desktop-linux >/dev/null 2>&1; then
  ok "Docker Desktop context exists: desktop-linux"
else
  fail "Docker Desktop context desktop-linux was not found. Install/open Docker Desktop first."
fi

if [ -e /dev/kvm ]; then
  ok "/dev/kvm exists"
else
  fail "/dev/kvm is missing. Docker Desktop needs KVM on Linux."
fi

if groups | grep -qw kvm; then
  ok "current session has kvm group"
else
  warn "current session does not show kvm group. Log out and back in after install."
fi

if groups | grep -qw docker; then
  ok "current session has docker group"
else
  warn "current session does not show docker group. Helper scripts can use sg docker when available."
fi

if docker --context desktop-linux info >/dev/null 2>&1; then
  ok "Docker Desktop daemon is reachable"
else
  warn "Docker Desktop daemon is not reachable yet. Start Docker Desktop from the app menu."
fi

for port in 5173 8000; do
  if ss -ltn "( sport = :$port )" | tail -n +2 | grep -q .; then
    warn "port $port is currently in use"
  else
    ok "port $port is free"
  fi
done
