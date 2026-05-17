# ESP32 ScAIdev captive-portal demo

Turns an Arduino Nano ESP32 into an open WiFi access point named
**`ScAIdev`** with a captive portal that auto-pops a landing page the
moment someone connects. The landing page is the **Recall Agent demo**
(Dutch UI, with audio scenarios). The original public-WiFi awareness
"gotcha" page is still on the device too, parked at `/gotcha`.

No credentials are collected. No traffic is logged.

## How it works

1. ESP32 broadcasts an open AP (default SSID: `ScAIdev`).
2. A built-in **DNS server** answers every domain lookup with the ESP32's
   own IP (`192.168.4.1`), so any URL resolves to the device.
3. The ESP32 responds to the OS-specific *captive portal probe* URLs
   (Android `/generate_204`, iOS `/hotspot-detect.html`, Windows
   `/connecttest.txt`, etc.) with a `302` redirect to `/`. This is what
   tells phones "you're behind a captive portal" — they then automatically
   pop the sign-in sheet showing your page.
4. Everything the page needs — HTML, fonts (Fraunces, Inter Tight,
   JetBrains Mono), and audio MP3s — lives in a **LittleFS** partition
   on the ESP32 and is served from `/`, `/fonts/`, and `/audio/`. The
   device works fully offline; no internet is required after flashing.

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
├── partitions.csv           # custom 16 MB layout with LittleFS partition
└── data/                    # everything in here is uploaded to LittleFS
    ├── index.html           # Recall Agent demo (served at /)
    ├── gotcha.html          # original awareness page (served at /gotcha)
    ├── fonts/               # locally hosted WOFF2s (Fraunces, Inter Tight, JetBrains Mono)
    │   ├── fraunces-{latin,latin-ext}.woff2
    │   ├── intertight-{latin,latin-ext}.woff2
    │   └── jetbrainsmono-{latin,latin-ext}.woff2
    └── audio/               # ElevenLabs scenario clips, verified playing on-device
        ├── scenario_logistical.mp3
        ├── scenario_medical.mp3
        ├── scenario_noanswer.mp3
        └── scenario_stop.mp3
```

### Why `partitions.csv` is here

The Nano ESP32's stock partition scheme (`app3M_fat9M_fact512k_16MB`)
allocates its 9 MB of data space to **FAT**, not SPIFFS/LittleFS, so the
`arduino-littlefs-upload` plugin can't find a partition to write to and
errors with `Partition entry not found in csv file!`.

Dropping a `partitions.csv` next to the sketch overrides the board's
default. Our custom scheme gives:

- 2 × 3 MB app partitions (OTA-capable)
- ~9.94 MB SPIFFS/LittleFS data partition

**You must re-upload the sketch (the firmware) after changing the
partition table.** Otherwise the running firmware still believes the old
partition layout exists and the LittleFS upload won't be visible.

Total `data/` payload is ~**3.6 MB** (mostly the four audio files). The
Nano ESP32's default partition scheme allocates ~4 MB to LittleFS, so it
fits with margin and is confirmed uploading/serving end-to-end. If you
add a lot more audio and the LittleFS upload starts failing with "No
space left on device," switch *Tools → Partition Scheme* to one that
gives the filesystem more room.

## Endpoints

- `GET /` — the Recall Agent demo (main landing page).
- `GET /gotcha` — the original public-WiFi awareness page.
- `GET /status` — JSON: SSID, IP, connected clients, lifetime visitor
  count, uptime.
- `GET /audio/scenario_*.mp3` — the scenario voice clips.
- `GET /fonts/*.woff2` — the local copies of the Google Fonts.
- Anything else — `302` to `/` (captive portal trick).

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

1. Show the audience the SSID list on their phones — point out `ScAIdev`.
2. A volunteer connects.
3. Within a second or two their phone auto-opens the Recall Agent demo —
   no browser, no typing.
4. Walk through the four scenarios (Logistiek / Medisch / Geen antwoord /
   Wil stoppen); each plays its ElevenLabs voice clip from LittleFS.
5. If you want to pivot to the public-WiFi awareness angle, point them
   at `http://192.168.4.1/gotcha`.
6. Volunteer disconnects. Done.
