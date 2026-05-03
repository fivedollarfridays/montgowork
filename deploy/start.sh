#!/usr/bin/env bash
set -euo pipefail

# Bring up Tailscale only if an auth key is supplied. Without it, the
# container still boots and the API runs (LLM calls fall back to mock).
if [[ -n "${TAILSCALE_AUTHKEY:-}" ]]; then
  echo "[start] starting tailscaled..."
  /usr/sbin/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &
  sleep 2
  /usr/bin/tailscale up \
    --authkey="${TAILSCALE_AUTHKEY}" \
    --hostname="${TAILSCALE_HOSTNAME:-montgowork-vibes}" \
    --accept-routes
  echo "[start] tailscale up"
else
  echo "[start] TAILSCALE_AUTHKEY not set — skipping tailscale, LLM will fall back to mock unless OPENAI_BASE_URL is reachable without it"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
