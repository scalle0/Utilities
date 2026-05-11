#!/usr/bin/env bash
# Start the ScAIdev captive-portal demo: brings up the AP, DHCP/DNS hijack,
# and the Flask landing app. Stops cleanly on Ctrl-C.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo ./start.sh"
  exit 1
fi

cd "$(dirname "$0")"

IFACE="$(awk -F= '/^interface=/{print $2; exit}' config/hostapd.conf)"
echo "Using AP interface: $IFACE"

cleanup() {
  echo
  echo "Shutting down..."
  pkill -P $$ || true
  ip addr flush dev "$IFACE" 2>/dev/null || true
  ip link set "$IFACE" down 2>/dev/null || true
  echo "Stopped. NetworkManager will reclaim $IFACE shortly."
}
trap cleanup EXIT INT TERM

# Free the interface from NetworkManager so hostapd can grab it.
nmcli device set "$IFACE" managed no 2>/dev/null || true

ip link set "$IFACE" down
ip addr flush dev "$IFACE"
ip addr add 192.168.4.1/24 dev "$IFACE"
ip link set "$IFACE" up

echo "Starting hostapd..."
hostapd config/hostapd.conf &
HOSTAPD_PID=$!

# Give hostapd a moment to bring up the AP before dnsmasq binds.
sleep 2

echo "Starting dnsmasq..."
dnsmasq --no-daemon --conf-file=config/dnsmasq.conf &
DNSMASQ_PID=$!

echo "Starting Flask landing app on port 80..."
python3 app.py &
FLASK_PID=$!

echo
echo "AP up. SSID: ScAIdev   Gateway: 192.168.4.1"
echo "Connect a phone and watch this terminal for visit logs."
echo "Ctrl-C to stop."

# Wait for any child to exit (and then cleanup runs via trap).
wait -n "$HOSTAPD_PID" "$DNSMASQ_PID" "$FLASK_PID"
