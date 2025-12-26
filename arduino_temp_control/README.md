# Arduino R4 WiFi Temperature Control System

Automated temperature control system using Arduino R4 WiFi with Modulino sensors, Arduino IoT Cloud dashboard, and Google Home integration.

## Features

- **Real-time Temperature Monitoring**: Uses Modulino Thermo sensor
- **Adjustable Temperature Thresholds**: Set your preferred temperature range (18-25°C) from the dashboard
- **Automatic Heater Control**:
  - Turns ON heater when temperature drops below your lower threshold (default 23°C)
  - Turns OFF heater when temperature rises above your upper threshold (default 24°C)
- **IoT Cloud Dashboard**: Control and monitor from anywhere
- **Google Home Integration**: Voice control and automation via Arduino Cloud triggers
- **Manual Override**: Use Modulino button or dashboard to disable automation
- **LED Matrix Display** ✨: Built-in 12x8 RGB matrix shows scrolling temperature and heater status
- **Optional LED Strip Control**: Add WS2812B LED strip for visual temperature indication (see [LED_FEATURES.md](LED_FEATURES.md))

## Hardware Requirements

- Arduino R4 WiFi
- Modulino Thermo (temperature sensor)
- Modulino Buttons (for manual control)
- Smart plug/socket compatible with Google Home (for heater control)

## Software Requirements

- Arduino IDE 2.0 or later
- Arduino IoT Cloud account (free tier available)
- Libraries:
  - ArduinoIoTCloud
  - Arduino_ConnectionHandler
  - Modulino

## Setup Instructions

### 1. Arduino IoT Cloud Setup

1. Go to [Arduino IoT Cloud](https://create.arduino.cc/iot/)
2. Create a new **Thing**
3. Associate your Arduino R4 WiFi device
4. Add the following Cloud Variables:

| Variable Name | Type | Permission | Description |
|--------------|------|------------|-------------|
| `currentTemperature` | float | Read Only | Current temperature reading |
| `autoControlEnabled` | boolean | Read & Write | Enable/disable automatic control |
| `heaterStatus` | boolean | Read Only | Current heater status |
| `manualHeaterControl` | boolean | Read & Write | Manual heater control |
| `tempThresholdLow` | float | Read & Write | Lower temperature threshold (18-25°C) |
| `tempThresholdHigh` | float | Read & Write | Upper temperature threshold (18-25°C) |

5. Configure your WiFi credentials in the Network section
6. Download your device credentials (Device ID and Secret Key)

### 2. Update Arduino Code

1. Open `thingProperties.h`
2. Update the following with your credentials:
```cpp
const char DEVICE_LOGIN_NAME[] = "YOUR_DEVICE_ID";
const char SSID[] = "YOUR_WIFI_SSID";
const char PASS[] = "YOUR_WIFI_PASSWORD";
const char DEVICE_KEY[] = "YOUR_DEVICE_KEY";
```

### 3. Install Required Libraries

In Arduino IDE:
1. Go to **Sketch → Include Library → Manage Libraries**
2. Install:
   - `ArduinoIoTCloud`
   - `Arduino_ConnectionHandler`
   - `Modulino`

### 4. Upload the Code

1. Connect your Arduino R4 WiFi to your computer
2. Select the correct board and port
3. Upload `arduino_temp_control.ino`
4. Open Serial Monitor (9600 baud) to see status messages

### 5. Create IoT Cloud Dashboard

1. In Arduino IoT Cloud, go to **Dashboards**
2. Create a new dashboard
3. Add widgets:
   - **Gauge**: Link to `currentTemperature` (displays current temp)
   - **Switch**: Link to `autoControlEnabled` (toggle automation on/off)
   - **LED**: Link to `heaterStatus` (shows heater state)
   - **Switch**: Link to `manualHeaterControl` (manual heater control)
   - **Slider** or **Value**: Link to `tempThresholdLow` (set lower temp, range 18-25, step 0.1)
   - **Slider** or **Value**: Link to `tempThresholdHigh` (set upper temp, range 18-25, step 0.1)

### 6. Google Home Integration (Arduino Cloud Automations)

**Recommended Method: Arduino IoT Cloud Triggers**

1. **Add smart plug to Google Home app** and name it "Heater"
2. **Link Google Home to Arduino Cloud**:
   - Arduino IoT Cloud → **Integrations** → Add **Google Home**
   - Authorize and sync your devices
3. **Create automation for ON**:
   - Arduino IoT Cloud → **Triggers** → Create Trigger
   - When: `heaterStatus` equals `true`
   - Then: Turn ON "Heater" (Google Home device)
4. **Create automation for OFF**:
   - Create another trigger
   - When: `heaterStatus` equals `false`
   - Then: Turn OFF "Heater" (Google Home device)

**Response time**: 1-2 seconds, completely free!

See **GOOGLE_HOME_SETUP.md** for detailed step-by-step instructions.

## Usage

### Automatic Mode (Default)

- System monitors temperature continuously
- When temp < 23°C: Heater turns ON
- When temp > 24°C: Heater turns OFF
- View status on IoT Cloud dashboard

### Disable Automation

**Method 1: Dashboard**
- Open Arduino IoT Cloud dashboard
- Toggle `autoControlEnabled` to OFF
- Use `manualHeaterControl` switch to control heater manually

**Method 2: Physical Button**
- Press Button A on Modulino Buttons to toggle automation on/off

### Temperature Thresholds

To modify temperature thresholds, edit in `arduino_temp_control.ino`:
```cpp
const float TEMP_THRESHOLD_LOW = 23.0;   // Turn heater ON below this
const float TEMP_THRESHOLD_HIGH = 24.0;  // Turn heater OFF above this
```

## Hysteresis Explained

The system uses a 1°C hysteresis band (23-24°C) to prevent rapid on/off cycling:
- Heater turns ON only when temp drops below 23°C
- Heater turns OFF only when temp rises above 24°C
- Between 23-24°C, heater maintains its current state

## Troubleshooting

### Arduino won't connect to WiFi
- Check SSID and password in `thingProperties.h`
- Ensure 2.4GHz WiFi (R4 WiFi doesn't support 5GHz)
- Check Serial Monitor for connection errors

### Temperature shows NaN
- Check Modulino Thermo connections
- Ensure `Modulino.begin()` is called before `thermo.begin()`
- Verify Modulino is properly seated on Arduino

### Google Home not responding
- Verify IFTTT applets are enabled
- Check that smart plug is connected to Google Home
- Test manual control from Google Home app first

### Cloud variables not updating
- Ensure Arduino is connected to IoT Cloud (check Serial Monitor)
- Verify device credentials are correct
- Check internet connection

## Code Structure

- `arduino_temp_control.ino` - Main sketch with control logic
- `thingProperties.h` - IoT Cloud configuration and credentials

## Security Notes

- Keep your `DEVICE_KEY` secret
- Don't commit credentials to public repositories
- Use WPA2/WPA3 secured WiFi networks

## License

This project is open source and available for personal and educational use.

## Support

For issues and questions:
- Arduino IoT Cloud: [Arduino Forum](https://forum.arduino.cc/)
- Modulino: [Modulino Documentation](https://docs.arduino.cc/hardware/modulino/)
- IFTTT: [IFTTT Help](https://help.ifttt.com/)
