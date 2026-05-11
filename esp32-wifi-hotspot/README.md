# ESP32 WiFi Hotspot

Turns an ESP32 into an **open** WiFi access point that also serves a small
status landing page at `http://192.168.4.1`.

## Prerequisites

- Arduino IDE (1.8.x or 2.x) **or** PlatformIO.
- ESP32 board support installed:
  - In Arduino IDE: *File → Preferences → Additional Board URLs* →
    `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
  - Then *Tools → Board → Boards Manager* → install **esp32 by Espressif Systems**.
- A USB cable that supports data (not charge-only).

No external libraries needed — `WiFi.h` and `WebServer.h` ship with the
ESP32 Arduino core.

## Configure

Open `esp32-wifi-hotspot.ino` and change the SSID at the top if desired:

```cpp
const char* AP_SSID = "ESP32-Hotspot";
```

The network is open (no password). If you want WPA2, change the call in
`setup()` from `WiFi.softAP(AP_SSID)` to
`WiFi.softAP(AP_SSID, "your-password")` (password must be 8+ chars).

## Flash

1. Plug the ESP32 in over USB.
2. *Tools → Board* → pick your ESP32 variant (e.g. *ESP32 Dev Module*).
3. *Tools → Port* → pick the serial port that appeared.
4. Click **Upload**.

## Use

1. Open the Serial Monitor at **115200 baud**. You should see:
   ```
   AP started
   SSID: ESP32-Hotspot
   IP:   192.168.4.1
   ```
2. On your phone or laptop, connect to the `ESP32-Hotspot` network.
3. Browse to `http://192.168.4.1` — the page shows SSID, AP IP, connected
   client count, and uptime, auto-refreshing every 5 seconds.
4. `GET /status` returns the same data as JSON, e.g.
   `curl http://192.168.4.1/status`.
