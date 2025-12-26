# LED Features Guide - Arduino R4 WiFi

The Arduino R4 WiFi has built-in LED features that enhance your temperature control system with visual feedback.

## Built-in LED Matrix (12x8 RGB)

### What It Does
- **Scrolls temperature** in real-time (e.g., "23.5C HEAT:OFF")
- **Updates every 5 seconds** with current readings
- **Shows heater status** (ON/OFF)
- **Color display** (white text on the RGB matrix)

### Dashboard Control
- **Switch widget** for `ledMatrixEnabled`
- Toggle ON/OFF from anywhere
- Turns off matrix to save power or reduce distraction

### What You'll See
```
Scrolling text on matrix:
"23.5C  HEAT:OFF  23.5C  HEAT:OFF  "

When heater is on:
"24.2C  HEAT:ON  24.2C  HEAT:ON  "
```

### No Extra Hardware Needed!
The LED matrix is built into the Arduino R4 WiFi board - just upload the code!

## Optional: External LED Strip

### What You Can Add
**WS2812B LED Strip** (NeoPixel compatible)
- Price: $5-15 for 1-5 meters
- Shows temperature as colors:
  - 🔵 **Blue** = Cold (below threshold)
  - 🟢 **Green** = Perfect (in range)
  - 🔴 **Red** = Hot (above threshold)
  - ⚪ **White** = Heater active

### Hardware Needed
1. **WS2812B LED Strip** (30-144 LEDs/meter)
   - Search: "WS2812B LED strip"
   - Price: $8-15 for 1 meter

2. **Power Supply** (if using >30 LEDs)
   - 5V power adapter
   - Calculate: ~60mA per LED at full brightness
   - Example: 30 LEDs = 1.8A, use 5V 2A adapter

3. **Wiring**
   - Data pin: Connect to Arduino R4 WiFi GPIO (e.g., D6)
   - Power: 5V and GND (from Arduino or external supply)
   - Capacitor: 1000µF across power (recommended)

### Software Setup

**1. Install Library**
```
Arduino IDE → Library Manager → Search "FastLED" → Install
```

**2. Add to Code**
Add at top of arduino_temp_control.ino:
```cpp
// Uncomment to enable LED strip support
//#define ENABLE_LED_STRIP
#define LED_STRIP_PIN 6        // GPIO pin for data
#define NUM_LEDS 30            // Number of LEDs in strip

#ifdef ENABLE_LED_STRIP
  #include <FastLED.h>
  CRGB leds[NUM_LEDS];
#endif
```

**3. Initialize in setup()**
```cpp
#ifdef ENABLE_LED_STRIP
  FastLED.addLeds<WS2812B, LED_STRIP_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);  // 0-255
#endif
```

**4. Update onLedStripEnabledChange()**
```cpp
void onLedStripEnabledChange() {
  Serial.print("LED Strip ");
  Serial.println(ledStripEnabled ? "ENABLED" : "DISABLED");

  #ifdef ENABLE_LED_STRIP
    if (ledStripEnabled) {
      // Set color based on temperature
      CRGB color;

      if (currentTemperature < tempThresholdLow) {
        color = CRGB::Blue;  // Too cold
      } else if (currentTemperature > tempThresholdHigh) {
        color = CRGB::Red;   // Too hot
      } else {
        color = CRGB::Green; // Just right
      }

      // Heater active = white
      if (heaterStatus) {
        color = CRGB::White;
      }

      // Set all LEDs to color
      fill_solid(leds, NUM_LEDS, color);
      FastLED.show();
    } else {
      // Turn off all LEDs
      fill_solid(leds, NUM_LEDS, CRGB::Black);
      FastLED.show();
    }
  #endif
}
```

### Wiring Diagram

```
Arduino R4 WiFi          WS2812B LED Strip

GPIO6 (D6) ──────────────► DIN (Data In)

5V ──────────────────────► 5V/VCC

GND ─────────────────────► GND

Optional for long strips:
External 5V PSU ─────────► VCC (parallel to strip)
External GND ────────────► GND (common ground with Arduino)
```

### Power Considerations

| LEDs | Current @ Full White | Power Supply Needed |
|------|---------------------|---------------------|
| 10 | 600mA | Arduino 5V OK |
| 30 | 1.8A | External 5V 2A |
| 60 | 3.6A | External 5V 4A |
| 144 | 8.6A | External 5V 10A |

**Rule of thumb**: 60mA per LED at full brightness

### Dashboard Control

Add in Arduino IoT Cloud dashboard:
- **Switch widget** → Link to `ledStripEnabled`
- Toggle ON/OFF to control LED strip
- Works with automation!

## Complete Feature List

### LED Matrix (Built-in) ✅
- [x] Real-time temperature display
- [x] Scrolling text animation
- [x] Heater status indicator
- [x] Dashboard on/off control
- [x] No extra hardware needed

### LED Strip (Optional) 🔧
- [ ] Temperature color coding
- [ ] Heater status (white when active)
- [ ] Dashboard on/off control
- [ ] Requires WS2812B strip
- [ ] Requires FastLED library

## Example Dashboard Layout

```
┌─────────────────────────────────┐
│  Temperature Control Dashboard  │
├─────────────────────────────────┤
│                                 │
│  [Gauge] Current Temp: 23.5°C   │
│                                 │
│  [Switch] Automation: ON        │
│  [LED] Heater Status: OFF       │
│  [Switch] Manual Control: OFF   │
│                                 │
│  [Slider] Min Temp: 23.0°C      │
│  [Slider] Max Temp: 24.0°C      │
│                                 │
│  [Switch] LED Matrix: ON  ✨    │
│  [Switch] LED Strip: OFF        │
│                                 │
└─────────────────────────────────┘
```

## Troubleshooting

### LED Matrix Not Working
```
Problem: Matrix stays blank

Solutions:
1. Check ledMatrixEnabled is ON in dashboard
2. Verify Serial Monitor shows temperature readings
3. Check #include "Arduino_LED_Matrix.h" in code
4. Re-upload sketch
```

### LED Strip Not Working
```
Problem: Strip doesn't light up

Solutions:
1. Check wiring: DIN to GPIO6, 5V to 5V, GND to GND
2. Verify #define ENABLE_LED_STRIP is uncommented
3. Check FastLED library is installed
4. Verify NUM_LEDS matches your strip
5. Test with example: File → Examples → FastLED → Blink
```

### LED Strip Wrong Colors
```
Problem: Colors are wrong (e.g., red shows as green)

Solution:
Change color order in FastLED.addLeds:
- Try: <WS2812B, LED_STRIP_PIN, GRB>
- Or: <WS2812B, LED_STRIP_PIN, RGB>
- Or: <WS2812B, LED_STRIP_PIN, BRG>
```

## Cost Breakdown

| Feature | Hardware Cost | Difficulty |
|---------|--------------|------------|
| LED Matrix | $0 (built-in) | Easy ⭐ |
| LED Strip (basic) | ~$10 | Medium ⭐⭐ |
| LED Strip (advanced) | ~$20 | Medium ⭐⭐ |

## Next Steps

### To Use LED Matrix Only (Recommended):
1. Upload updated code
2. Add 2 new cloud variables in IoT Cloud:
   - `ledMatrixEnabled` (boolean, READ/WRITE)
   - `ledStripEnabled` (boolean, READ/WRITE)
3. Add switch widgets to dashboard
4. Enjoy scrolling temperature display!

### To Add LED Strip:
1. Buy WS2812B LED strip
2. Install FastLED library
3. Uncomment #define ENABLE_LED_STRIP in code
4. Wire strip to Arduino
5. Upload code
6. Toggle ledStripEnabled on dashboard

Happy LED lighting! ✨🌡️
