#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${UNO_CHAT_MODEL:-qwen2.5:1.5b}"
PORT="${UNO_CHAT_PORT:-8080}"

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "[run] Starting 'ollama serve' in the background..."
  nohup ollama serve >/tmp/ollama.log 2>&1 &
  for _ in $(seq 1 20); do
    sleep 1
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
  done
fi

cd "$HERE/server"
# shellcheck disable=SC1091
. .venv/bin/activate
exec env UNO_CHAT_MODEL="$MODEL" \
  uvicorn app:app --host 0.0.0.0 --port "$PORT"
