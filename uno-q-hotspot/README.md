# UNO Q — Public-WiFi Awareness Demo (Linux edition)

Same demo, recreated using **real** open-source AP infrastructure on the
UNO Q's Linux side: `hostapd` for the access point, `dnsmasq` for DHCP +
DNS hijack, a small **Flask** app for the landing page. Because we have
a real OS, the page can show each visitor **what the network just learned
about them** &mdash; their IP, MAC, vendor guess, browser fingerprint, and
preferred languages &mdash; live, the moment they connect.

This is the "and this is what real attackers actually use" version of
the demo. The MCU sketches show the *idea*; this one shows the
*plumbing*.

## What it does

- `hostapd` broadcasts an open AP named `ScAIdev` on `wlan0`.
- `dnsmasq` hands out DHCP leases in `192.168.4.0/24` and answers every
  DNS query with `192.168.4.1` (the captive-portal trick).
- Flask app on port 80 serves a captive-portal page that introspects
  each request and shows the visitor what their phone leaked just by
  joining.
- All visitor metadata is logged to `state.json` next to the app and
  shown at `/status` as JSON.

## What it does *not* do

- No credential prompts.
- No traffic capture beyond standard HTTP request headers.
- No upstream internet pass-through &mdash; the AP is intentionally a
  dead end. Phones will mark it "no internet" after a few seconds; that
  is the expected demo flow.

## Layout

```
uno-q-hotspot/
├── README.md
├── setup.sh                 # one-time install
├── start.sh                 # bring AP up and run the app
├── app.py                   # Flask landing app
├── templates/
│   └── index.html
└── config/
    ├── hostapd.conf
    └── dnsmasq.conf
```

## Prerequisites

- Arduino UNO Q with its stock Linux image (Debian-based).
- A wireless interface that supports AP mode. Check with:
  ```
  iw list | grep -A 8 "Supported interface modes"
  ```
  You want `AP` in the listed modes. The UNO Q's onboard WiFi chip
  supports this; most USB dongles based on `rt8188eu`/`rtl8192cu` do
  not.
- Root access (the demo needs to bind ports 53/80 and reconfigure the
  WiFi interface).

## Setup

```
sudo ./setup.sh
```

Installs `hostapd`, `dnsmasq`, `python3-flask`, and disables the
system-wide hostapd/dnsmasq services so they don't auto-start on boot.

## Configure

Find your wireless interface name:

```
ip link
```

Look for something like `wlan0`, `wlp1s0`, or `wlan1`. Then edit:

- `config/hostapd.conf` &rarr; set `interface=` to that name
- `config/dnsmasq.conf`  &rarr; set `interface=` to the same name

## Run

```
sudo ./start.sh
```

The script:

1. Takes the interface back from NetworkManager.
2. Assigns it `192.168.4.1/24`.
3. Starts `hostapd` (the AP).
4. Starts `dnsmasq` (DHCP + DNS hijack).
5. Starts the Flask landing app on port 80.

Ctrl-C cleanly stops all three and returns the interface to
NetworkManager.

## Verify

From another device:

1. Scan for WiFi &mdash; `ScAIdev` should appear, no padlock.
2. Connect. Phone should pop the captive portal sheet within ~2 s.
3. The page shows the visitor's MAC, vendor guess, User-Agent, etc.

On the UNO Q itself:

```
curl http://192.168.4.1/status
```

Returns JSON with total visitor count and recent visits.

## Reset the visitor log

```
rm state.json
```

## Ethics

This is a real, working open access point with a real DNS hijack. The
**ethics rules from the other demos still apply, and more strictly:**

- Run it only on networks/hardware you control, with audiences who know
  what they're seeing.
- **Do not** name it after a real venue or known SSID.
- **Do not** add internet pass-through (e.g. NAT to a second interface)
  unless you understand that doing so makes the device into a real MITM
  position and significantly increases your legal liability.
- If you wouldn't be comfortable showing this terminal to a network
  engineer at the venue, don't run it there.

The point is to teach awareness, not to phish anyone.
