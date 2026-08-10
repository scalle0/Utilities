# Hardware Setup Guide

Complete guide for assembling your Arduino R4 WiFi temperature control system with Modulino sensors.

## Required Components

### Main Components
- **Arduino R4 WiFi** (1x)
- **Modulino Thermo** (1x) - Temperature sensor module
- **Modulino Buttons** (1x) - Button interface module
- **Modulino Base** (1x) - Connection board for Modulinos

### Power & Connectivity
- **USB-C cable** - For programming and power
- **5V USB power adapter** (optional for standalone operation)

### Smart Home Components
- **Smart plug compatible with Google Home** (1x)
  - Recommended brands: TP-Link Kasa, Wemo, Gosund, Tapo
  - Must support Google Home integration
- **Heater** - Your existing heater that plugs into the smart socket

## Assembly Instructions

### Step 1: Modulino Base Setup

1. **Attach Modulino Base to Arduino R4 WiFi**
   ```
   - Locate the Qwiic/I2C connector on Arduino R4 WiFi
   - Connect Modulino Base to Arduino using included cable
   - Or mount Modulinos on compatible Arduino carrier board
   ```

2. **Modulino Connection Points**
   ```
   The Modulino system uses I2C communication:
   - SDA (Data line)
   - SCL (Clock line)
   - VCC (Power - 3.3V)
   - GND (Ground)
   ```

### Step 2: Connect Modulino Thermo

1. **Physical Connection**
   ```
   - Take Modulino Thermo module
   - Connect to first Qwiic port on Modulino Base
   - Or daisy-chain using Qwiic cable
   - Ensure connections are firm
   ```

2. **Verify Connection**
   ```
   - Modulino Thermo has built-in temperature sensor
   - No additional wiring needed
   - LED on module indicates power
   ```

### Step 3: Connect Modulino Buttons

1. **Physical Connection**
   ```
   - Take Modulino Buttons module
   - Connect to next available Qwiic port
   - Can be chained after Modulino Thermo
   ```

2. **Button Functions**
   ```
   - Button A (0): Toggle automation on/off
   - Buttons B, C (optional for future features)
   ```

## Wiring Diagram (Text-based)

```
┌─────────────────────────────┐
│   Arduino R4 WiFi           │
│                             │
│  ┌─────────┐               │
│  │ I2C/    │               │
│  │ Qwiic   │               │
│  └────┬────┘               │
│       │                     │
└───────┼─────────────────────┘
        │ Qwiic Cable
        │
    ┌───▼────────────┐
    │ Modulino Base  │
    │                │
    │ Port 1  Port 2 │
    └───┬───────┬────┘
        │       │
        │       └──────────────┐
        │                      │
┌───────▼──────┐      ┌────────▼────────┐
│  Modulino    │      │   Modulino      │
│  Thermo      │      │   Buttons       │
│              │      │                 │
│  [Sensor]    │      │  [A] [B] [C]    │
└──────────────┘      └─────────────────┘

                ┌────────────────┐
WiFi )))  ◄────►│  Arduino R4    │
Cloud           │  IoT Cloud     │
                └────────────────┘
                        │
                        │ IFTTT/Webhook
                        ▼
                ┌────────────────┐
                │  Google Home   │
                └────────┬───────┘
                         │
                         ▼
                ┌────────────────┐
                │  Smart Plug    │◄──── AC Power
                └────────┬───────┘
                         │
                         ▼
                   [Heater]
```

## Power Setup

### Development/Testing
```
Arduino R4 WiFi powered via USB-C from computer
- Provides 5V for Arduino
- Powers Modulinos via I2C bus
- Serial Monitor available for debugging
```

### Standalone Operation
```
Arduino R4 WiFi powered via USB-C from wall adapter
- Use 5V 2A USB power adapter
- Place Arduino near WiFi router for best signal
- No computer needed once programmed
```

## Smart Plug Placement

### Optimal Setup
```
1. Plug smart plug into wall outlet
2. Plug heater into smart plug
3. Place heater in room to be heated
4. Place Arduino with Modulino Thermo:
   - In same room as heater
   - Away from heater's direct heat
   - At average room height (not floor/ceiling)
   - Good WiFi signal strength
```

### Placement Tips
```
✓ DO:
- Place sensor at breathing height (3-5 feet)
- Avoid direct sunlight
- Avoid heat sources (heater, PC, windows)
- Ensure good air circulation around sensor
- Keep away from doors/windows (drafts)

✗ DON'T:
- Place directly in heater airflow
- Mount on cold exterior walls
- Place in direct sunlight
- Put in enclosed spaces
```

## I2C Address Information

The Modulino modules use I2C communication with default addresses:

```
Modulino Thermo:  0x28 (default)
Modulino Buttons: 0x6B (default)
```

If you have I2C conflicts, addresses can be changed via solder jumpers on modules.

## Testing the Hardware

### Step 1: Power On
```
1. Connect Arduino via USB
2. LEDs should light up on Arduino and Modulinos
3. Open Arduino IDE Serial Monitor (9600 baud)
```

### Step 2: Verify Modulino Communication
```
Expected Serial Output:
"Arduino R4 WiFi Temperature Control Starting..."
"Modulino devices initialized"
"Temperature: XX.X °C"
```

### Step 3: Test Button
```
1. Press Button A on Modulino Buttons
2. Should see: "Automation DISABLED" or "Automation ENABLED"
3. LED may flash on button press
```

### Step 4: Test Temperature Reading
```
1. Observe temperature in Serial Monitor
2. Touch Modulino Thermo sensor (gently)
3. Temperature should increase slightly
4. Wait - temperature should return to ambient
```

## Troubleshooting Hardware Issues

### No Temperature Reading (shows NaN)
```
Problem: Temperature shows "NaN" in Serial Monitor

Solutions:
1. Check I2C connections
   - Ensure Qwiic cable is firmly seated
   - Try different cable

2. Verify power
   - Check LED on Modulino Thermo is lit
   - Try USB power from different port

3. Check I2C address
   - Run I2C scanner sketch to detect devices
   - Verify address matches code (0x28)

4. Re-seat modules
   - Disconnect and reconnect Modulinos
   - Power cycle Arduino
```

### Button Not Responding
```
Problem: Pressing Button A doesn't toggle automation

Solutions:
1. Check connection
   - Verify Modulino Buttons is connected
   - Check Qwiic cable

2. Test with Serial Monitor
   - Watch for button press messages
   - May need debounce adjustment

3. Verify I2C address
   - Default should be 0x6B
   - Run I2C scanner if needed
```

### WiFi Won't Connect
```
Problem: Arduino can't connect to WiFi network

Solutions:
1. Check credentials in thingProperties.h
   - SSID must match exactly (case-sensitive)
   - Password must be correct

2. Verify network compatibility
   - Arduino R4 WiFi only supports 2.4GHz
   - WPA2/WPA3 supported
   - Guest networks may block IoT devices

3. Improve signal strength
   - Move Arduino closer to router
   - Check for interference
   - Use WiFi analyzer to find best channel
```

### Arduino IoT Cloud Won't Connect
```
Problem: WiFi works but cloud connection fails

Solutions:
1. Verify device credentials
   - DEVICE_LOGIN_NAME correct
   - DEVICE_KEY correct
   - Check Arduino IoT Cloud dashboard

2. Check library versions
   - Update ArduinoIoTCloud library
   - Update Arduino_ConnectionHandler

3. Debug output
   - Look for error codes in Serial Monitor
   - Check Arduino IoT Cloud status page
```

## Enclosure Ideas

### Recommended Enclosures
```
1. 3D Printed Case
   - Search "Arduino R4 WiFi case" on Thingiverse
   - Add cutouts for Modulino cables
   - Include ventilation for temperature sensor

2. Project Box
   - Small plastic project box (100x60x25mm)
   - Drill holes for USB and Qwiic cables
   - Add ventilation holes near sensor

3. Open Frame
   - Simple acrylic mounting plate
   - Standoffs for Arduino
   - Keeps sensor exposed to air
```

### Ventilation Requirements
```
IMPORTANT: Temperature sensor needs airflow!

- Don't fully seal enclosure
- Add ventilation holes/slots
- Keep sensor exposed or near opening
- Avoid creating heat pockets
```

## Maintenance

### Regular Checks
```
Weekly:
- Verify temperature readings seem accurate
- Check WiFi connection status
- Test button functionality

Monthly:
- Clean dust from sensor area (gentle brush)
- Check cable connections
- Verify smart plug responds correctly
```

### Sensor Calibration
```
If temperature seems off:
1. Compare with known-good thermometer
2. Add calibration offset in code if needed:
   float temp = thermo.getTemperature() + CALIBRATION_OFFSET;
3. Typical accuracy: ±0.5°C
```

## Safety Notes

⚠️ **Important Safety Information**

1. **Electrical Safety**
   - Only qualified persons should work with mains voltage
   - Smart plug handles AC power - Arduino handles low voltage only
   - Keep Arduino away from water/moisture

2. **Heater Safety**
   - Ensure heater is appropriate for smart plug wattage rating
   - Don't exceed smart plug capacity (typically 10-15A)
   - Use heater with safety features (tip-over, overheat protection)
   - Never leave heater unattended for extended periods

3. **Fire Safety**
   - Don't cover heater or block airflow
   - Keep flammable materials away from heater
   - Consider adding smoke detector to room
   - Test automation thoroughly before leaving unattended

## Next Steps

After hardware assembly:
1. Follow README.md for software setup
2. Upload and test the Arduino sketch
3. Configure Arduino IoT Cloud dashboard
4. Set up Google Home integration (GOOGLE_HOME_SETUP.md)
5. Test the complete system before deploying
