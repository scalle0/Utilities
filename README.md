# Utilities
Used by scalle0 to code energy management system in the house.
try to get growatt

## Projects

### Public-WiFi awareness demos

Three flavors of the same lesson — joining a stranger's open WiFi can hand
over more than you think — implemented on three different boards so the
audience can see the same idea built three different ways:

- [esp32-wifi-hotspot](esp32-wifi-hotspot/) — **Arduino Nano ESP32.** Captive
  portal + landing page on LittleFS, persistent visitor counter, RGB LED
  reacts to each new connection. The cute, portable version.
- [uno-r4-wifi-hotspot](uno-r4-wifi-hotspot/) — **Arduino UNO R4 WiFi.** Same
  lesson, hand-rolled HTTP + DNS hijack on top of `WiFiS3`, and the onboard
  12x8 LED matrix scrolls `GOTCHA` on each new visit. The theatrical version.
- [uno-q-hotspot](uno-q-hotspot/) — **Arduino UNO Q.** Real-deal Linux stack
  with `hostapd` + `dnsmasq` + Flask. Landing page shows the visitor what
  their phone leaked (MAC, vendor, browser fingerprint, languages) the
  moment they joined. The serious version.

