# ESP32 Temperature Control System

Budget-friendly automated temperature control using ESP32, standard temperature sensors, and Google Home integration via Arduino IoT Cloud.

## Why ESP32 Version?

**Cost Comparison:**
- Arduino R4 WiFi + Modulino: **~$85+**
- ESP32 + Standard Sensors: **~$25-30** ✅ **Save $55!**

**Same Features:**
- ✅ Arduino IoT Cloud integration
- ✅ Google Home control
- ✅ Adjustable temperature thresholds (18-25°C)
- ✅ Mobile dashboard control
- ✅ Automatic heater control

## Quick Start

**Total cost: ~$31** | **Setup time: ~45 minutes**

### What You Need to Buy

| Item | Recommended | Price |
|------|-------------|-------|
| ESP32 Board | ESP32 DevKit V1 | $6 |
| Temperature Sensor | DS18B20 Waterproof | $3 |
| Button | 12mm Tactile (20-pack) | $2 |
| Resistors | 4.7kΩ + 10kΩ kit | $3 |
| Breadboard | 830 point | $3 |
| Jumper Wires | Male-to-Male 65pcs | $2 |
| USB Cable | Micro USB | $2 |
| Smart Plug | Gosund (Google Home) | $10 |

**Total: ~$31** (see [PARTS_LIST.md](PARTS_LIST.md) for detailed shopping guide)

## Features

- **Real-time Temperature Monitoring**: DS18B20 (±0.5°C) or DHT22 sensor
- **Adjustable Temperature Thresholds**: Set 18-25°C range from dashboard with 0.1°C precision
- **Automatic Heater Control**:
  - Turns ON when temperature < lower threshold (default 23°C)
  - Turns OFF when temperature > upper threshold (default 24°C)
- **IoT Cloud Dashboard**: Monitor and control from anywhere via phone/web
- **Google Home Integration**: Voice control via Arduino Cloud automations
- **Physical Button**: Manual override to toggle automation
- **Built-in LED**: Visual status indicator

## Hardware Requirements

### Required
- **ESP32 Development Board** (any variant: DevKit, WROOM, etc.)
- **Temperature Sensor** (choose one):
  - DS18B20 waterproof digital sensor (recommended)
  - DHT22 temperature & humidity sensor
- **Push Button**: 12mm tactile button or button module
- **Resistors**:
  - 4.7kΩ (for DS18B20 pull-up)
  - 10kΩ (optional for button, can use internal pull-up)
- **Breadboard** and jumper wires
- **USB cable** (Micro USB or USB-C depending on board)
- **Smart plug** compatible with Google Home

### Optional
- Project enclosure
- Additional buttons
- Multiple DS18B20 sensors (for multiple rooms)

## Software Requirements

- **Arduino IDE** 2.0 or later
- **Arduino IoT Cloud** account (free tier)
- **Libraries** (install via Arduino IDE Library Manager):
  - `ArduinoIoTCloud`
  - `Arduino_ConnectionHandler`
  - `DallasTemperature` (for DS18B20)
  - `OneWire` (for DS18B20)
  - `DHT sensor library` (for DHT22)

## Setup Instructions

### 1. Hardware Assembly

See [WIRING_GUIDE.md](WIRING_GUIDE.md) for detailed wiring instructions.

**Quick Wiring Summary:**

**DS18B20 Sensor:**
- RED → 3V3
- YELLOW → GPIO4
- BLACK → GND
- 4.7kΩ resistor between 3V3 and GPIO4

**Button:**
- One pin → GPIO5
- Other pin → GND
- (Uses internal pull-up)

**Built-in LED:** GPIO2 (automatic status indicator)

### 2. Arduino IoT Cloud Setup

1. Go to [create.arduino.cc/iot](https://create.arduino.cc/iot)
2. Create new **Thing**
3. Add ESP32 device
4. Add 6 Cloud Variables:

| Variable Name | Type | Permission | Description |
|--------------|------|------------|-------------|
| `currentTemperature` | float | Read | Current temp reading |
| `autoControlEnabled` | bool | Read/Write | Enable/disable automation |
| `heaterStatus` | bool | Read | Current heater status |
| `manualHeaterControl` | bool | Read/Write | Manual heater control |
| `tempThresholdLow` | float | Read/Write | Lower threshold (18-25°C) |
| `tempThresholdHigh` | float | Read/Write | Upper threshold (18-25°C) |

5. Configure WiFi credentials
6. Download device credentials (Device ID and Secret Key)

### 3. Configure Code

1. **Copy template:**
   ```bash
   cp thingProperties_template.h thingProperties.h
   ```

2. **Edit `thingProperties.h`** with your credentials:
   ```cpp
   const char DEVICE_LOGIN_NAME[] = "your-device-id";
   const char SSID[] = "YourWiFiName";
   const char PASS[] = "YourWiFiPassword";
   const char DEVICE_KEY[] = "your-secret-key";
   ```

3. **Select sensor** in `esp32_temp_control.ino`:
   ```cpp
   #define USE_DS18B20    // Uncomment for DS18B20
   //#define USE_DHT22      // Uncomment for DHT22
   ```

4. **Adjust pins** if needed (in esp32_temp_control.ino):
   ```cpp
   #define TEMP_SENSOR_PIN 4  // GPIO for sensor
   #define BUTTON_PIN 5       // GPIO for button
   ```

### 4. Upload Code

1. Connect ESP32 via USB
2. In Arduino IDE:
   - Select board: **ESP32 Dev Module** (or your specific board)
   - Select correct COM port
   - Upload sketch
3. Open Serial Monitor (115200 baud)
4. Verify:
   - "Found X sensors" (for DS18B20)
   - Temperature readings appear
   - WiFi connects to IoT Cloud

### 5. Create Dashboard

1. Arduino IoT Cloud → **Dashboards** → Create New
2. Add widgets:
   - **Gauge**: `currentTemperature` (shows temp)
   - **Switch**: `autoControlEnabled` (toggle automation)
   - **LED Indicator**: `heaterStatus` (heater state)
   - **Switch**: `manualHeaterControl` (manual control)
   - **Slider**: `tempThresholdLow` (min: 18, max: 25, step: 0.1)
   - **Slider**: `tempThresholdHigh` (min: 18, max: 25, step: 0.1)

### 6. Google Home Integration

1. **Add smart plug to Google Home app**, name it "Heater"
2. **Link Google Home to Arduino Cloud**:
   - Arduino IoT Cloud → Integrations → Google Home
   - Authorize and sync devices
3. **Create trigger for ON**:
   - Triggers → Create
   - When: `heaterStatus` = `true`
   - Then: Turn ON "Heater"
4. **Create trigger for OFF**:
   - When: `heaterStatus` = `false`
   - Then: Turn OFF "Heater"

**Response time: 1-2 seconds, completely free!**

## Usage

### Automatic Mode (Default)
- System monitors temperature every 5 seconds
- When temp < `tempThresholdLow` (23°C): Heater ON
- When temp > `tempThresholdHigh` (24°C): Heater OFF
- Visual feedback via built-in LED

### Manual Control Methods

**1. Physical Button:**
- Press button → Toggles automation ON/OFF
- LED blinks twice to confirm
- Works without internet!

**2. Dashboard Switch:**
- Toggle `autoControlEnabled` → Enable/disable automation
- When OFF, use `manualHeaterControl` to control heater directly

**3. Adjust Thresholds:**
- Drag sliders on dashboard to set preferred temperature range
- Changes apply immediately
- Range: 18.0 - 25.0°C with 0.1°C precision

## Troubleshooting

### Temperature Shows NaN
- Check sensor wiring (see WIRING_GUIDE.md)
- Verify 4.7kΩ pull-up resistor (DS18B20)
- Check Serial Monitor: "Found 0 sensors" means wiring issue

### WiFi Won't Connect
- Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
- Check SSID and password in thingProperties.h
- Move ESP32 closer to router

### Button Not Working
- Verify button connected between GPIO5 and GND
- Check Serial Monitor for "Button pressed" message
- LED should blink when button pressed

### Google Home Not Responding
- Verify Integration is linked in Arduino Cloud
- Check both triggers are enabled
- Ensure smart plug is online in Google Home app

## Advanced Features

### Multiple Temperature Sensors
DS18B20 supports multiple sensors on one pin!
- Connect all sensors to same GPIO4 pin
- Share VCC, GND, and single 4.7kΩ pull-up
- Modify code to read all sensors

### Custom Temperature Range
Change range in code:
```cpp
// In callback functions, change:
if (tempThresholdLow < 15.0)  // Was 18.0
if (tempThresholdLow > 30.0)  // Was 25.0
```

### Different Sensor Pins
Change in code:
```cpp
#define TEMP_SENSOR_PIN 15  // Use GPIO15 instead
#define BUTTON_PIN 16       // Use GPIO16 instead
```

## Files Overview

| File | Purpose |
|------|---------|
| `esp32_temp_control.ino` | Main sketch - upload to ESP32 |
| `thingProperties_template.h` | Credentials template |
| `PARTS_LIST.md` | Complete shopping guide |
| `WIRING_GUIDE.md` | Detailed wiring instructions |
| `README.md` | This file |
| `.gitignore` | Prevents committing credentials |

## Safety Notes

⚠️ **Important:**
- ESP32 GPIO pins are 3.3V only (NOT 5V tolerant!)
- Always use appropriate heater wattage for smart plug
- Test automation thoroughly before leaving unattended
- Heater should have tip-over and overheat protection
- Never exceed smart plug capacity (typically 10-15A)

## Comparison: ESP32 vs Arduino R4 WiFi

| Feature | ESP32 Version | Arduino R4 + Modulino |
|---------|--------------|----------------------|
| **Total Cost** | ~$31 | ~$90+ |
| **Main Board** | $6 | $30 |
| **Temp Sensor** | $3-6 | $20 (Modulino) |
| **Buttons** | $0.50-3 | $20 (Modulino) |
| **WiFi** | Built-in | Built-in |
| **Setup Difficulty** | Medium | Easy (plug-and-play) |
| **Flexibility** | High (any sensor) | Limited (Modulino only) |
| **Cloud Integration** | Arduino IoT Cloud | Arduino IoT Cloud |
| **Google Home** | Yes | Yes |

**ESP32 = 66% cheaper, more flexible!**

## Supported Sensors

### Temperature Only
- ✅ DS18B20 (recommended - waterproof, accurate)
- ✅ DS18B20 regular (non-waterproof)
- ✅ LM35 (analog, requires code changes)

### Temperature + Humidity
- ✅ DHT22 (AM2302)
- ✅ DHT11 (less accurate, cheaper)
- ✅ BME280 (also pressure, I2C)

**Note:** Code includes DS18B20 and DHT22 support. For other sensors, modify `readTemperature()` function.

## License

Open source - free for personal and educational use.

## Support

- **Arduino Forum**: [forum.arduino.cc](https://forum.arduino.cc)
- **ESP32 Community**: [esp32.com](https://esp32.com)
- **Arduino IoT Cloud Help**: [docs.arduino.cc](https://docs.arduino.cc/arduino-cloud/)

## Acknowledgments

Based on Arduino R4 WiFi + Modulino version with adaptations for:
- Standard ESP32 boards
- Common affordable sensors (DS18B20, DHT22)
- Budget-conscious makers

---

**Ready to build? Start with [PARTS_LIST.md](PARTS_LIST.md) to order components!** 🛒

**Need wiring help? See [WIRING_GUIDE.md](WIRING_GUIDE.md) for detailed diagrams!** 🔌

**Questions? Check troubleshooting section above!** ❓

Happy making! 🌡️🏠
