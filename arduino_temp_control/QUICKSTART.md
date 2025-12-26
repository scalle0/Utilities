# Quick Start Guide

Get your Arduino temperature control system running in 30 minutes!

## Prerequisites Checklist

- [ ] Arduino R4 WiFi
- [ ] Modulino Thermo
- [ ] Modulino Buttons
- [ ] USB-C cable
- [ ] Smart plug (Google Home compatible)
- [ ] WiFi network (2.4GHz)
- [ ] Arduino IoT Cloud account
- [ ] Google Home app installed

## 5-Step Setup

### Step 1: Hardware Assembly (5 minutes)

1. Connect Modulino Thermo and Buttons to Arduino R4 WiFi via Qwiic cables
2. Connect Arduino to computer via USB-C
3. Plug smart plug into wall outlet
4. Plug heater into smart plug

**See HARDWARE_SETUP.md for detailed wiring**

### Step 2: Create Arduino IoT Cloud Thing (5 minutes)

1. Go to [create.arduino.cc/iot](https://create.arduino.cc/iot)
2. Create new Thing
3. Add your Arduino R4 WiFi device
4. Add 4 Cloud Variables:
   - `currentTemperature` (float, READ)
   - `autoControlEnabled` (boolean, READ/WRITE)
   - `heaterStatus` (boolean, READ)
   - `manualHeaterControl` (boolean, READ/WRITE)
5. Set WiFi credentials
6. Download device credentials

### Step 3: Configure & Upload Code (10 minutes)

1. Open `thingProperties.h`
2. Add your credentials:
   ```cpp
   const char DEVICE_LOGIN_NAME[] = "your-device-id";
   const char SSID[] = "YourWiFiName";
   const char PASS[] = "YourWiFiPassword";
   const char DEVICE_KEY[] = "your-secret-key";
   ```

3. Install libraries in Arduino IDE:
   - ArduinoIoTCloud
   - Arduino_ConnectionHandler
   - Modulino

4. Open `arduino_temp_control.ino`
5. Upload to Arduino R4 WiFi
6. Open Serial Monitor (9600 baud) to verify

### Step 4: Set Up Dashboard (5 minutes)

1. In Arduino IoT Cloud, create new Dashboard
2. Add widgets:
   - **Gauge**: `currentTemperature`
   - **Switch**: `autoControlEnabled`
   - **LED**: `heaterStatus`
   - **Switch**: `manualHeaterControl`
3. Save dashboard

### Step 5: Connect Google Home (5 minutes)

1. **Add smart plug to Google Home app** and name it "Heater"
2. **Link Google Home to Arduino Cloud**:
   - Arduino IoT Cloud → Integrations → Add Google Home
   - Authorize and sync devices
3. **Create trigger for ON**:
   - Arduino IoT Cloud → Triggers → Create
   - When: `heaterStatus` = `true`
   - Then: Turn ON "Heater"
4. **Create trigger for OFF**:
   - Create another trigger
   - When: `heaterStatus` = `false`
   - Then: Turn OFF "Heater"

**Fast and free! No IFTTT needed. See GOOGLE_HOME_SETUP.md for detailed instructions**

## Test Your System

### Test 1: Manual Control
1. Open IoT Cloud dashboard
2. Toggle `autoControlEnabled` to OFF
3. Toggle `manualHeaterControl` to ON
4. Heater should turn on within 1-2 seconds!

### Test 2: Automatic Control
1. Toggle `autoControlEnabled` to ON
2. Watch current temperature on dashboard
3. If temp < 23°C, heater should turn ON
4. If temp > 24°C, heater should turn OFF

### Test 3: Button Control
1. Press Button A on Modulino Buttons
2. Should toggle automation on/off
3. Check Serial Monitor for confirmation

## Default Behavior

### Temperature Control
- **Below 23°C**: Heater turns ON
- **Above 24°C**: Heater turns OFF
- **Between 23-24°C**: Maintains current state

### Control Methods
1. **Automatic** (default): Based on temperature thresholds
2. **Manual**: Via dashboard when automation disabled
3. **Button**: Press Button A to toggle auto mode

## Customization

### Change Temperature Thresholds

Edit in `arduino_temp_control.ino`:
```cpp
const float TEMP_THRESHOLD_LOW = 23.0;   // Your preferred lower temp
const float TEMP_THRESHOLD_HIGH = 24.0;  // Your preferred upper temp
```

### Change Update Frequency

Edit in `arduino_temp_control.ino`:
```cpp
const unsigned long TEMP_READ_INTERVAL = 5000;  // milliseconds
```

## Common Issues & Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| WiFi won't connect | Check SSID/password, ensure 2.4GHz network |
| Temperature shows NaN | Check Modulino connections, power cycle |
| Cloud won't connect | Verify device credentials, check internet |
| Google Home not responding | Check Integration is linked, verify triggers enabled |
| Button not working | Check Modulino Buttons connection |

## File Reference

- **arduino_temp_control.ino** - Main code
- **thingProperties.h** - Your credentials (keep secret!)
- **README.md** - Complete documentation
- **HARDWARE_SETUP.md** - Wiring and assembly
- **GOOGLE_HOME_SETUP.md** - Google integration
- **config_template.h** - Advanced configuration options

## Safety Reminders

⚠️ **Before leaving system unattended:**
- Test for at least 24 hours while present
- Verify heater has tip-over protection
- Ensure smart plug rating > heater wattage
- Check that automation works correctly
- Never block heater airflow

## Next Steps

1. ✅ System running? Monitor for 24 hours
2. 📊 Check temperature logs in IoT Cloud
3. 🎚️ Adjust thresholds to your comfort
4. 🏠 Create Google Home routines
5. 🔔 Set up alerts for temperature extremes (optional)

## Getting Help

- **Hardware issues**: See HARDWARE_SETUP.md troubleshooting
- **Cloud issues**: Check Arduino IoT Cloud forum
- **Google Home issues**: See GOOGLE_HOME_SETUP.md
- **Code questions**: Check comments in .ino file

## What's Next?

### Optional Enhancements
- Add humidity sensor
- Create scheduling (weekday vs weekend temps)
- Add temperature history graph
- Implement email/SMS alerts
- Add multiple rooms/zones

Enjoy your automated temperature control! 🌡️🏠
