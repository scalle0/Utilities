# ESP32 Temperature Control - Wiring Guide

Complete wiring instructions for connecting your temperature sensor and buttons to ESP32.

## Pin Configuration

Default pin assignments (you can change these in the code):

| Component | ESP32 Pin | Notes |
|-----------|-----------|-------|
| DS18B20 Data | GPIO4 | 1-Wire data line (needs 4.7kΩ pull-up) |
| DHT22 Data | GPIO4 | Digital data line |
| Button | GPIO5 | Uses internal pull-up resistor |
| Status LED | GPIO2 | Built-in LED on most ESP32 boards |
| Power (3.3V) | 3V3 | For sensors |
| Ground | GND | Common ground |

##

 Option 1: DS18B20 Waterproof Sensor (Recommended)

### Parts Needed
- ESP32 board
- DS18B20 waterproof temperature sensor
- 4.7kΩ resistor (usually included with sensor)
- Breadboard
- Jumper wires

### Wiring Diagram

```
DS18B20 Sensor Wiring:
┌─────────────────┐
│  DS18B20        │
│  (3 wires)      │
└────┬──┬──┬──────┘
     │  │  │
  RED│ YEL│ BLK│
     │  │  │
   VCC  │ GND
     │  │  │
     │  └──┼──────────┐
     │     │          │
     │  ┌──▼────┐     │
     │  │ 4.7kΩ │     │
     │  └──┬────┘     │
     │     │          │
┌────▼─────▼──────────▼────┐
│    ESP32                 │
│                          │
│  3V3  GPIO4        GND   │
└──────────────────────────┘
```

### Step-by-Step Connection

**1. Identify DS18B20 Wires:**
   - **RED** → VCC (Power +3.3V)
   - **YELLOW** → DATA (Signal)
   - **BLACK** → GND (Ground)

**2. Connect to ESP32:**
   - RED wire → 3V3 pin on ESP32
   - YELLOW wire → GPIO4 on ESP32
   - BLACK wire → GND on ESP32

**3. Add Pull-up Resistor:**
   - One end of 4.7kΩ resistor → 3V3 pin
   - Other end of 4.7kΩ resistor → GPIO4 pin (same as DATA line)

**Note**: Many waterproof DS18B20 sensors come with the resistor already built-in. Check your sensor's documentation.

### Breadboard Layout

```
         ESP32 DevKit
    ┌────────────────────┐
 3V3├─────┬──────────────┤
    │     │              │
    │  ┌──▼────┐         │
    │  │4.7kΩ R│         │
    │  └──┬────┘         │
    │     │              │
GPIO4├─────┴──────────────┤ ← DATA (Yellow)
    │                    │
  GND├────────────────────┤
    └────────────────────┘
         │         │
        RED      BLACK
      (DS18B20)
```

## Option 2: DHT22 Sensor Module

### Parts Needed
- ESP32 board
- DHT22 sensor (preferably on module/breakout board)
- Breadboard
- Jumper wires
- 10kΩ resistor (if using bare sensor, not needed for modules)

### Wiring Diagram

```
DHT22 Module (3-pin):
┌─────────────────┐
│   DHT22         │
│  [  Module  ]   │
└──┬────┬────┬────┘
   │    │    │
   VCC DATA GND
   │    │    │
┌──▼────▼────▼─────┐
│    ESP32         │
│                  │
│ 3V3 GPIO4  GND   │
└──────────────────┘
```

### Step-by-Step Connection

**For DHT22 Module (3 pins):**
   - VCC (or +) → 3V3 on ESP32
   - DATA (or OUT/S) → GPIO4 on ESP32
   - GND (or -) → GND on ESP32

**For Bare DHT22 Sensor (4 pins, looking at the grid):**
   - Pin 1 (VCC) → 3V3 on ESP32
   - Pin 2 (DATA) → GPIO4 on ESP32
   - Pin 3 (NC) → Not connected
   - Pin 4 (GND) → GND on ESP32
   - 10kΩ resistor between Pin 1 and Pin 2 (pull-up)

## Button Wiring

### Parts Needed
- 1x Tactile push button (12mm)
- 1x 10kΩ resistor (optional - can use internal pull-up)
- Jumper wires

### Wiring Diagram (Using Internal Pull-up)

```
┌──────────────────┐
│   Button         │
│   [    ]         │
└──┬────────┬──────┘
   │        │
   │     (not used)
   │
┌──▼─────────────────┐
│  ESP32             │
│                    │
│ GPIO5        GND   │
└──┬─────────────┬───┘
   │             │
   └─────[BTN]───┘

When pressed: GPIO5 connects to GND (LOW)
When not pressed: GPIO5 is pulled HIGH by internal resistor
```

### Step-by-Step Connection

**Simple Method (Using Internal Pull-up):**
1. Connect one pin of button → GPIO5
2. Connect other pin of button → GND
3. Code enables internal pull-up resistor
4. When pressed, pin reads LOW; when not pressed, pin reads HIGH

**Alternative Method (External Pull-up Resistor):**
1. Connect one pin of button → GPIO5
2. Connect other pin of button → GND
3. Connect 10kΩ resistor between GPIO5 and 3V3
4. Same behavior as internal pull-up

## Complete Wiring - All Components

### Full System with DS18B20

```
                    ┌──────────────────────────┐
                    │      ESP32 DevKit        │
                    │                          │
         ┌──────────┤ 3V3                      │
         │       ┌──┤ GPIO4 (DS18B20)          │
         │       │  ├─ GPIO5 (Button)  ───┐    │
         │       │  │                     │    │
         │       │  ├─ GPIO2 (LED) Built-in    │
         │       │  │                          │
      ┌──┴───┐   │  ├─ GND ─────────┬─────┬───┘
      │4.7kΩ │   │  │               │     │
      └──┬───┘   │  └───────────────┼─────┼────
         │       │                  │     │
         └───────┴──────────────────┘     │
          │                │              │
        [DS18B20]        [BUTTON]         │
      RED YEL BLK                         │
       │   │   └─────────────────────────┘
       │   └─────────────────────────────┘
       └─────────────────────────────────┘
```

### Breadboard Layout Example

```
    ESP32 Board (Top View)
    ═══════════════════════
    │                     │
 3V3├○  ┌──────────┐     │
    │   │ 4.7kΩ    │     │
GPIO4├○──┴──────────●─────┤ ← To DS18B20 Yellow
GPIO5├○─────────────●─────┤ ← To Button
GPIO2├● (Built-in LED)    │
  GND├○───●───●───────────┤
    │    │   │           │
    └────┼───┼───────────┘
         │   │
     Button  DS18B20 Black
```

## Power Considerations

### ESP32 Power Requirements
- Operating Voltage: 3.3V (regulated on board)
- Input Voltage: 5V via USB or VIN pin
- Current Draw: ~80mA (active WiFi)

### Sensor Power
- **DS18B20**: 1mA (typical), up to 1.5mA
- **DHT22**: 1-1.5mA (typical), up to 2.5mA

### Total System
- ESP32 + Sensor: ~82-85mA
- USB port can easily supply this (500mA typical)
- No external power supply needed for development/testing

## Troubleshooting Wiring Issues

### Temperature Sensor Not Detected

**For DS18B20:**
```
Problem: "Found 0 DS18B20 sensors" in Serial Monitor

Solutions:
1. Check 4.7kΩ pull-up resistor is connected
2. Verify wiring: RED=3V3, YELLOW=GPIO4, BLACK=GND
3. Try different GPIO pin
4. Test sensor with multimeter (should show ~resistance on DATA line)
5. Some sensors need 5V instead of 3.3V (check datasheet)
```

**For DHT22:**
```
Problem: "Error reading DHT22 sensor!" continuously

Solutions:
1. Check connections: VCC, DATA, GND
2. Verify DATA line is connected to GPIO4
3. Wait 2+ seconds between readings (DHT22 is slow)
4. Check if using DHT11 instead of DHT22 (change in code)
5. Try external 10kΩ pull-up resistor
```

### Button Not Working

```
Problem: Button press doesn't toggle automation

Solutions:
1. Check button is connected between GPIO5 and GND
2. Verify button is actually pressing (test with multimeter)
3. Check Serial Monitor for "Button pressed" message
4. Try external 10kΩ pull-up resistor
5. Swap button (might be defective)
```

### WiFi Won't Connect

```
Problem: ESP32 can't connect to WiFi

Solutions:
1. Check SSID and password in thingProperties.h
2. Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
3. Move ESP32 closer to router
4. Check router settings (WPA2 Personal recommended)
5. Try hotspot from phone to test
```

## Advanced: Multiple Temperature Sensors

DS18B20 supports multiple sensors on same pin!

### Wiring Multiple DS18B20

```
All sensors share same 3 wires:
- All RED → 3V3
- All YELLOW → GPIO4 (with single 4.7kΩ pull-up)
- All BLACK → GND

┌──────┐  ┌──────┐  ┌──────┐
│DS#1  │  │DS#2  │  │DS#3  │
└┬──┬─┬┘  └┬──┬─┬┘  └┬──┬─┬┘
 │  │ │    │  │ │    │  │ │
 └──┼─┴────┴──┼─┴────┴──┼─┘
    │         │         │
 ┌──▼─────────▼─────────▼──┐
 │  4.7kΩ                  │
 └──┬──────────────────────┘
    │
┌───▼─────────────┐
│ ESP32           │
│ 3V3  GPIO4  GND │
└─────────────────┘
```

**Code changes needed:**
```cpp
// Read all sensors
sensors.requestTemperatures();
float temp1 = sensors.getTempCByIndex(0);  // First sensor
float temp2 = sensors.getTempCByIndex(1);  // Second sensor
float temp3 = sensors.getTempCByIndex(2);  // Third sensor
```

## Safety Notes

⚠️ **Important Safety Information**

1. **Power Safety**
   - Only use 3.3V for sensors (ESP32 pins are NOT 5V tolerant!)
   - Don't connect 5V directly to GPIO pins
   - Use regulated power supply if not using USB

2. **Wiring Safety**
   - Double-check polarity before powering on
   - Avoid short circuits between VCC and GND
   - Disconnect power when changing wiring

3. **ESD Protection**
   - ESP32 is sensitive to static electricity
   - Touch grounded metal before handling
   - Consider anti-static mat for assembly

## Testing Your Wiring

### Step-by-Step Test

**1. Visual Inspection**
   - [ ] All connections secure
   - [ ] No loose wires
   - [ ] Correct polarity (VCC, GND)
   - [ ] Pull-up resistor in place

**2. Power Test**
   - [ ] Plug in ESP32 via USB
   - [ ] Built-in LED should blink during boot
   - [ ] Check voltage at sensor VCC pin (should be ~3.3V)

**3. Sensor Test**
   - [ ] Upload code
   - [ ] Open Serial Monitor (115200 baud)
   - [ ] Should see "Found X sensors" (DS18B20)
   - [ ] Should see temperature readings every 5 seconds

**4. Button Test**
   - [ ] Press button
   - [ ] Should see "Button pressed" in Serial Monitor
   - [ ] LED should blink twice
   - [ ] Automation should toggle

**5. Full System Test**
   - [ ] Temperature reads correctly
   - [ ] Button toggles automation
   - [ ] Cloud connection works
   - [ ] Dashboard shows values

## Pin Reference Card

Print this for easy reference while wiring:

```
┌───────────────────────────────────────┐
│   ESP32 TEMPERATURE CONTROL PINS      │
├───────────────────────────────────────┤
│ COMPONENT    │ ESP32 PIN  │ NOTES    │
├───────────────────────────────────────┤
│ DS18B20 VCC  │ 3V3        │ Red      │
│ DS18B20 DATA │ GPIO4      │ Yellow   │
│ DS18B20 GND  │ GND        │ Black    │
│ Pull-up 4.7k │ 3V3-GPIO4  │          │
├───────────────────────────────────────┤
│ DHT22 VCC    │ 3V3        │          │
│ DHT22 DATA   │ GPIO4      │          │
│ DHT22 GND    │ GND        │          │
├───────────────────────────────────────┤
│ Button Pin 1 │ GPIO5      │          │
│ Button Pin 2 │ GND        │          │
├───────────────────────────────────────┤
│ Status LED   │ GPIO2      │ Built-in │
└───────────────────────────────────────┘
```

Cut along the dotted line and keep near your workbench!

---

## Next Steps

Once wiring is complete:
1. Upload the sketch
2. Open Serial Monitor (115200 baud)
3. Verify all components working
4. Proceed to IoT Cloud setup

For complete setup instructions, see **README.md**

Happy wiring! 🔌
