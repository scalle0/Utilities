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
4. The landing page itself is just static HTML with security tips.

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

## Prerequisites

- Arduino IDE (1.8.x or 2.x) or PlatformIO.
- ESP32 board support — *Boards Manager* → install **esp32 by Espressif Systems**.
- No external libraries; `WiFi.h`, `WebServer.h`, and `DNSServer.h` all
  ship with the ESP32 Arduino core.

## Configure

Edit the top of `esp32-wifi-hotspot.ino`:

```cpp
const char* AP_SSID    = "ScAIdev";
const char* DEMO_OWNER = "Your friendly neighborhood demo";
```

`DEMO_OWNER` is the sign-off shown at the bottom of the landing page —
put your name, your meetup, your company, whatever.

## Flash

1. Plug the ESP32 in over USB.
2. *Tools → Board* → your ESP32 variant (e.g. *ESP32 Dev Module*).
3. *Tools → Port* → the serial port that appeared.
4. **Upload**.
5. Open Serial Monitor at **115200 baud**. Expected:
   ```
   Captive demo AP started
   SSID: ScAIdev
   IP:   192.168.4.1
   ```

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
