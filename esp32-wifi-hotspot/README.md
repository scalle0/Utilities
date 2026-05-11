# ESP32 Public-WiFi Awareness Demo

Turns an ESP32 into an open WiFi access point named **`ScAIdev`** with a
**captive portal** that auto-pops a tongue-in-cheek "gotcha" page the moment
someone connects. The
landing page explains what an attacker on a rogue hotspot *could* do and
how to stay safer.

No credentials are collected. No traffic is logged. The whole point is the
landing page.

## How it works

1. ESP32 broadcasts an open AP (default SSID: `ScAIdev`).
2. A built-in **DNS server** answers every domain lookup with the ESP32's
   own IP (`192.168.4.1`), so any URL resolves to the device.
3. The ESP32 responds to the OS-specific *captive portal probe* URLs
   (Android `/generate_204`, iOS `/hotspot-detect.html`, Windows
   `/connecttest.txt`, etc.) with a `302` redirect to `/`. This is what
   tells phones "you're behind a captive portal" — they then automatically
   pop the sign-in sheet showing your page.
4. The landing page lives in `data/index.html` and is served from a
   **LittleFS** partition on the ESP32 — you upload it once, separately
   from the sketch, and you can edit it without recompiling.

## Ethics & legality — read this

This is fine for:

- A talk, classroom, or meetup where the audience knows what's happening.
- Your own home, office, or event space.
- Personal experimentation in an RF-isolated setup.

This is **not** fine and likely illegal in many places:

- Impersonating a real network (`Starbucks WiFi`, `BTOpenzone`, an
  airline's onboard SSID, your neighbor's network name).
- Running it in a public space where unsuspecting strangers will join
  and you have no relationship with them.
- Adding any kind of credential prompt, even "just for the demo." That
  crosses from awareness into phishing.

When in doubt: get explicit consent from the venue and audience.

## Layout

```
esp32-wifi-hotspot/
├── esp32-wifi-hotspot.ino   # the sketch (firmware)
└── data/
    └── index.html           # the landing page (uploaded to LittleFS)
```

The `data/` folder is the convention used by the Arduino tooling — anything
in there becomes the contents of the ESP32's LittleFS partition.

## Hardware

Tested on an **Arduino Nano ESP32** (ESP32-S3 inside, PCB antenna on the
module — no external antenna or extra parts needed). Any other ESP32 dev
board with WiFi will also work; just pick the matching entry in
*Tools → Board*.

## Prerequisites

- **Arduino IDE 2.x** (recommended) or PlatformIO.
- The **Arduino ESP32 board package** — *Boards Manager* → install
  **esp32 by Espressif Systems** (v2.0+). On a fresh Arduino IDE 2.x,
  installing the *Arduino Nano ESP32* board through *Boards Manager* will
  also pull in the Espressif core automatically.
- The **LittleFS upload plugin** for Arduino IDE 2.x:
  [arduino-littlefs-upload](https://github.com/earlephilhower/arduino-littlefs-upload).
  Install instructions are in that repo's README — usually it's just
  dropping a `.vsix` file into `~/.arduinoIDE/plugins/`.
  (PlatformIO users: skip this, you already have `platformio run --target uploadfs`.)
- No external Arduino libraries; `WiFi.h`, `WebServer.h`, `DNSServer.h`,
  and `LittleFS.h` all ship with the ESP32 Arduino core.

## Configure

Two things you can edit independently:

1. **The SSID** — top of `esp32-wifi-hotspot.ino`:
   ```cpp
   const char* AP_SSID = "ScAIdev";
   ```
2. **The page** — `data/index.html`. Open it in any editor (or your
   browser, for live preview) and change whatever you like.

## Flash — two upload steps

You upload the sketch and the filesystem **separately**. Both go to the
ESP32 over the same USB cable, just via different menu items.

### 1. Upload the sketch (firmware)

1. Plug the board in over USB-C.
2. *Tools → Board* → **Arduino Nano ESP32** (or your ESP32 variant).
3. *Tools → Port* → the serial port that appeared.
4. *Tools → Partition Scheme* → leave on the default. The Nano ESP32's
   default scheme already reserves a LittleFS partition; if you ever
   switch to a "no FS" scheme the filesystem upload will fail.
5. Click **Upload** (the arrow button).

### 2. Upload the filesystem (the HTML page)

Arduino IDE 2.x, with the plugin installed:

1. Make sure the Serial Monitor is **closed** (it holds the port open).
2. `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) → type
   **"Upload LittleFS to Pico/ESP8266/ESP32"** → Enter.
3. Watch the bottom panel for "Hard resetting via RTS pin..." — done.

PlatformIO:

```
pio run --target uploadfs
```

You only need to redo this step when you change `data/index.html` — the
sketch itself doesn't need re-uploading.

### Verify

Open Serial Monitor at **115200 baud**. Expected:

```
Captive demo AP started
SSID: ScAIdev
IP:   192.168.4.1
```

If you see `LittleFS mount failed` or browsing `/` returns
`index.html missing from LittleFS`, you forgot step 2 — upload the
filesystem.

## Demo flow

1. Show the audience the SSID list on their phones — point out yours.
2. Have a volunteer connect to `ScAIdev`.
3. Within a second or two their phone auto-opens the landing page. No
   browser, no typing.
4. Read it out loud, walk through the safety tips.
5. Have the volunteer disconnect. Done.

## Endpoints

- `GET /` — the gotcha page.
- `GET /status` — JSON with SSID, IP, connected client count, uptime
  (handy for debugging from your laptop while running the demo).
- Anything else — `302` to `/`.
