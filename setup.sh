#!/usr/bin/env bash
set -euo pipefail

MODEL="${UNO_CHAT_MODEL:-qwen2.5:1.5b}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v ollama >/dev/null 2>&1; then
  echo "[setup] Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "[setup] Ollama already installed: $(ollama --version 2>/dev/null || true)"
fi

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "[setup] Starting 'ollama serve' in the background..."
  nohup ollama serve >/tmp/ollama.log 2>&1 &
  for _ in $(seq 1 20); do
    sleep 1
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
  done
fi

echo "[setup] Pulling model: $MODEL"
ollama pull "$MODEL"

echo "[setup] Setting up Python venv..."
cd "$HERE/server"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

cat <<EOF

[setup] Done.

Start the chat server with:
  $HERE/run.sh

Then on any device on the same WiFi, open:
  http://<uno-q-ip>:8080
EOF
