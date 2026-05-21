// Uno Q MCU-side bridge firmware.
//
// Exposes RPC methods to the Linux side via Arduino_RouterBridge.
// Bridge owns Serial1 (routed through /var/run/arduino-router.sock by
// the arduino-router daemon). Wire format is MessagePack-RPC.
//
// Required libraries (install via Library Manager):
//   - Arduino_RouterBridge

#include <Arduino_RouterBridge.h>

void setup() {
  Bridge.begin();

  Bridge.provide("ping", []() -> String {
    return String("pong");
  });

  Bridge.provide("gpio_mode", [](int pin, String mode) -> bool {
    if (mode == "input")             pinMode(pin, INPUT);
    else if (mode == "input_pullup") pinMode(pin, INPUT_PULLUP);
    else if (mode == "output")       pinMode(pin, OUTPUT);
    else return false;
    return true;
  });

  Bridge.provide("gpio_read", [](int pin) -> int {
    return digitalRead(pin);
  });

  Bridge.provide("gpio_write", [](int pin, bool value) -> bool {
    digitalWrite(pin, value ? HIGH : LOW);
    return true;
  });
}

void loop() {
  // Bridge runs its update on a dedicated thread; nothing to do here.
}
