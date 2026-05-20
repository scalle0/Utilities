#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="$(id -un)"
GROUP_NAME="$(id -gn)"
UNIT_PATH="/etc/systemd/system/uno-chat.service"

if [ ! -x "$HERE/run.sh" ]; then
  echo "Error: $HERE/run.sh not found or not executable. Did setup.sh run?" >&2
  exit 1
fi

echo "[install-service] Writing $UNIT_PATH"
sudo tee "$UNIT_PATH" >/dev/null <<EOF
[Unit]
Description=Uno Q Chat (local LLM web chatbot)
After=network-online.target ollama.service
Wants=network-online.target ollama.service

[Service]
Type=simple
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$HERE
ExecStart=$HERE/run.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "[install-service] Reloading systemd"
sudo systemctl daemon-reload

echo "[install-service] Enabling and starting uno-chat.service"
sudo systemctl enable --now uno-chat.service

sleep 2
sudo systemctl --no-pager --full status uno-chat.service || true

cat <<EOF

[install-service] Done. The chatbot will now start automatically at boot.

Useful commands:
  sudo systemctl status uno-chat       # current status
  sudo systemctl restart uno-chat      # restart after code changes
  sudo systemctl stop uno-chat         # stop
  sudo systemctl disable uno-chat      # don't start at boot
  sudo journalctl -u uno-chat -f       # live logs
EOF
