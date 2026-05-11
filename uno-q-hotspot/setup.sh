#!/usr/bin/env bash
# One-time setup for the ScAIdev captive-portal demo on the UNO Q.
# Installs hostapd, dnsmasq, python3-flask. Run once after flashing the
# UNO Q's Linux image. Re-runnable; apt is idempotent.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo ./setup.sh"
  exit 1
fi

echo "[1/3] Installing packages..."
apt-get update
apt-get install -y hostapd dnsmasq python3 python3-flask iproute2

echo "[2/3] Disabling system-wide hostapd/dnsmasq services."
echo "      We launch them on-demand via start.sh so they don't fight"
echo "      with NetworkManager or systemd-resolved when you're not"
echo "      running the demo."
systemctl stop hostapd dnsmasq 2>/dev/null || true
systemctl disable hostapd dnsmasq 2>/dev/null || true

echo "[3/3] Done."
echo
echo "Next: edit config/hostapd.conf and config/dnsmasq.conf so the"
echo "      'interface=' line matches your WiFi interface (check with"
echo "      'ip link'). Then run: sudo ./start.sh"
