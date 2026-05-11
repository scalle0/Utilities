# UNO R4 WiFi — Public-WiFi Awareness Demo

Same lesson as the [`esp32-wifi-hotspot/`](../esp32-wifi-hotspot/) project,
but ported to the **Arduino UNO R4 WiFi** with one extra trick: the onboard
**12x8 LED matrix** scrolls `GOTCHA` on each new visit and shows the
running visitor count in idle.

## Why a separate sketch?

The R4 WiFi's WiFi is provided by an ESP32-S3 co-processor that the main
Renesas RA4M1 talks to via the **`WiFiS3`** library. That library is not
the same as the ESP32 Arduino core. In particular it doesn't ship with a
`WebServer` class, a `DNSServer`, or a filesystem like LittleFS, so this
sketch hand-rolls:

- A tiny HTTP request parser on top of `WiFiServer` (top of file).
- A minimal DNS responder on top of `WiFiUDP` that answers every query
  with the AP's own IP &mdash; this is what makes phones pop the captive
  portal sheet on connect.
- The HTML landing page as a `PROGMEM` string at the bottom of the
  sketch (no filesystem upload step needed).
- A `uint32_t` visitor count persisted in the R4's onboard EEPROM.

## Hardware

- Arduino UNO R4 WiFi (the variant with onboard ESP32-S3 + LED matrix).
- USB-C cable. No external antenna; the ESP32-S3 module has a PCB antenna.

## Prerequisites

- **Arduino IDE 2.x**.
- *Boards Manager* → install **Arduino UNO R4 Boards** (Renesas + WiFiS3).
- No external libraries; `WiFiS3.h`, `WiFiUdp.h`, `EEPROM.h`, and
  `Arduino_LED_Matrix.h` all ship with the R4 board package.

## Flash

1. Plug the R4 in over USB-C.
2. *Tools → Board* → **Arduino UNO R4 WiFi**.
3. *Tools → Port* → the port that appeared.
4. Click **Upload**.
5. Open Serial Monitor at **115200 baud**. Expected:
   ```
   Loaded visitor count: 0
   Starting AP: ScAIdev
   AP IP: 192.168.4.1
   Captive demo AP listening.
   ```
6. The matrix displays `0` (the visitor count).

## Demo flow

1. Show the audience the matrix &mdash; "this is the running tally."
2. Volunteer joins `ScAIdev` on their phone.
3. The matrix scrolls **GOTCHA** for ~2.5 seconds, then settles on `1`.
4. The phone auto-opens the gotcha page.
5. Each subsequent connection ticks the matrix counter up.

## Reset the visitor count

The count survives reboots (it's in EEPROM). To reset to zero, easiest is
to add a one-liner to `setup()` temporarily:

```cpp
totalVisitors = 0; persistCount();
```

Upload once, then remove it and re-upload.

## Differences vs the ESP32 version

| Feature                 | ESP32 sketch                       | R4 sketch                                |
|-------------------------|------------------------------------|------------------------------------------|
| Landing page storage    | LittleFS (`data/index.html`)       | `PROGMEM` string in the `.ino`           |
| Visitor counter         | NVS (Preferences library)          | EEPROM at address 0                      |
| Visitor event detection | `ARDUINO_EVENT_WIFI_AP_STACONNECTED` | First HTTP request to `/`              |
| HTTP server             | `WebServer` library                | Hand-rolled on `WiFiServer`              |
| DNS hijack              | `DNSServer` library                | Hand-rolled DNS responder on `WiFiUDP`   |
| Visual feedback         | Onboard RGB LED                    | Onboard 12x8 LED matrix                  |

## Ethics

Same rules as the ESP32 version &mdash; see the parent README. Open APs
for awareness demos are fine in your own venues with informed audiences.
Don't impersonate real networks. No credentials are collected.
