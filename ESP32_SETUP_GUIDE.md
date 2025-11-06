# ESP32 Battery Controller Setup Guide

## 🎯 Overview

This guide shows you how to implement the battery automation system on an **ESP32** microcontroller instead of a PC/Raspberry Pi for 24/7 operation.

### Why ESP32 instead of Arduino?

| Feature | Arduino Uno/Nano | ESP32 | Raspberry Pi |
|---------|------------------|-------|--------------|
| Price | ~€5 | ~€8 | ~€40 |
| WiFi | ❌ No | ✅ Built-in | ✅ Yes |
| Memory | 2KB RAM | 520KB RAM | 1-8GB RAM |
| Processing | 16MHz | 240MHz dual-core | 1.5GHz quad-core |
| Power | ~50mA | ~160mA | ~500mA |
| Real-time clock | ❌ | ✅ (via NTP) | ✅ |
| Modbus support | Limited | ✅ Excellent | ✅ Full |
| **Best for** | Simple tasks | **This project** | Complex tasks |

**Verdict:** ESP32 is perfect for this - has WiFi, enough power, low cost, and runs 24/7 reliably!

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  PC/Server      │         │    ESP32     │         │    Growatt      │
│                 │         │              │         │    Inverter     │
│ - Fetch prices  │  WiFi   │ - Web UI     │  RS485  │                 │
│ - Optimize      │────────>│ - Schedule   │────────>│ - Battery       │
│ - Send schedule │  HTTP   │ - Modbus     │ Modbus  │ - Charging      │
│                 │         │ - Execute    │         │                 │
└─────────────────┘         └──────────────┘         └─────────────────┘
```

**How it works:**
1. PC runs optimization (once daily, can be your laptop)
2. PC sends optimized schedule to ESP32 via WiFi
3. ESP32 stores schedule and applies it to Growatt via Modbus
4. ESP32 runs 24/7, PC only needed for optimization

## 🛒 Hardware Shopping List

### Required Components

| Item | Purpose | Price | Where to Buy |
|------|---------|-------|--------------|
| **ESP32 Dev Board** | Main controller | €5-10 | Amazon, AliExpress |
| **MAX485 Module** | RS485 interface | €1-2 | Amazon, AliExpress |
| **Micro USB Cable** | Power for ESP32 | €2-5 | Any electronics store |
| **Jumper Wires** | Connections | €2-3 | Amazon, AliExpress |
| **5V Power Supply** | ESP32 power | €3-5 | Any phone charger works |

**Optional:**
- Enclosure/Case: €3-5
- LED indicators: €1-2
- Prototype board: €2-3

**Total Cost: €15-30** (vs €40+ for Raspberry Pi!)

### Recommended ESP32 Board

Look for: **ESP32-WROOM-32** or **ESP32 DevKitC**

Features needed:
- ✅ WiFi
- ✅ Dual UART (Serial2 for Modbus)
- ✅ GPIO pins
- ✅ USB programming

## 🔌 Wiring Diagram

```
ESP32 Board               MAX485 Module              Growatt Inverter
┌─────────────┐          ┌──────────────┐           ┌────────────────┐
│             │          │              │           │                │
│  3.3V   ────┼─────────>│ VCC          │           │                │
│             │          │              │           │                │
│  GND    ────┼─────────>│ GND          │           │                │
│             │          │              │           │    RS485       │
│  GPIO16 ────┼─────────>│ RO (RX)      │           │    Port        │
│  (RX2)      │          │              │           │   ┌─────────┐  │
│             │          │              │           │   │ A     B │  │
│  GPIO17 ────┼─────────>│ DI (TX)      │           │   └─────────┘  │
│  (TX2)      │          │              │           │                │
│             │          │            A ├───────────┼───> A          │
│  GPIO4  ────┼─────────>│ DE           │           │                │
│             │          │            B ├───────────┼───> B          │
│         ────┼─────────>│ RE           │           │                │
│             │          │              │           │                │
└─────────────┘          └──────────────┘           └────────────────┘
    │                                                        │
    │                                                        │
    └────────── Common GND ─────────────────────────────────┘
```

### Connection Details

**ESP32 to MAX485:**
- ESP32 3.3V → MAX485 VCC
- ESP32 GND → MAX485 GND
- ESP32 GPIO16 (RX2) → MAX485 RO
- ESP32 GPIO17 (TX2) → MAX485 DI
- ESP32 GPIO4 → MAX485 DE (and RE tied together)

**MAX485 to Growatt:**
- MAX485 A → Growatt RS485 A
- MAX485 B → Growatt RS485 B
- Common GND between all devices

**Important Notes:**
- ⚠️ Some Growatt inverters use **isolated RS485** - check your manual
- ⚠️ Polarity matters: A to A, B to B
- ⚠️ Cable length: Keep under 10m for best results
- ⚠️ Use twisted pair cable for RS485 (CAT5/6 works great)

## 📥 Software Installation

### 1. Install Arduino IDE

Download from: https://www.arduino.cc/en/software

### 2. Add ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "ESP32"
6. Install "ESP32 by Espressif Systems"

### 3. Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

- **ModbusMaster** by Doc Walker (for Modbus communication)
- **ArduinoJson** by Benoit Blanchon (for JSON parsing)

### 4. Upload the Sketch

1. Open `arduino/GrowattBatteryController/GrowattBatteryController.ino`

2. **Edit WiFi credentials:**
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   ```

3. **Adjust timezone:**
   ```cpp
   const long GMT_OFFSET_SEC = 3600;  // Your timezone in seconds
   ```

4. **Select board:**
   - **Tools → Board → ESP32 Arduino → ESP32 Dev Module**

5. **Select port:**
   - **Tools → Port → (your ESP32 COM port)**

6. **Upload:**
   - Click the **Upload** button (→)

### 5. Verify Upload

Open **Tools → Serial Monitor** (115200 baud)

You should see:
```
=== Growatt Battery Controller ===
Version 1.0
Connecting to WiFi: YourSSID
✓ WiFi connected
IP address: 192.168.1.50
✓ NTP configured
✓ Modbus initialized
✓ Web server started

=== Initialization Complete ===
Access web interface at: http://192.168.1.50
```

## 🌐 Web Interface

Once ESP32 is running, open a browser and go to:
```
http://192.168.1.50
```
(Use the IP address shown in Serial Monitor)

### Features:

- **Battery Status**: Real-time SOC, voltage, power
- **Current Schedule**: View active charging windows
- **Manual Control**: Refresh data, fetch new schedules
- **API Access**: JSON endpoints for integration

### API Endpoints:

```
GET  /api/status    - Get battery status (JSON)
GET  /api/schedule  - Get current schedule (JSON)
POST /api/schedule  - Upload new schedule (JSON)
```

## 🔧 Integration with Python System

### Option 1: Manual Upload

1. Run optimization on your PC:
   ```bash
   python3 battery_automation.py run
   ```

2. This creates: `battery_data/schedule_YYYYMMDD_HHMMSS.json`

3. Upload to ESP32 manually via web interface or:
   ```bash
   curl -X POST http://192.168.1.50/api/schedule \
     -H "Content-Type: application/json" \
     -d @battery_data/schedule_latest.json
   ```

### Option 2: Automatic via ESP32 Bridge

**Edit `battery_config.json`:**
```json
{
  "growatt": {
    "connection_type": "esp32",
    "esp32_ip": "192.168.1.50",
    "esp32_port": 80,
    "dry_run": false
  }
}
```

**Run automation:**
```bash
python3 battery_automation.py run
```

The system will:
1. Fetch prices
2. Optimize schedule
3. **Automatically send to ESP32**
4. ESP32 applies to Growatt

### Option 3: Hybrid Approach (Recommended)

Run Python script on a schedule (e.g., from your laptop daily at 13:00):

**Windows Task Scheduler:**
```
Program: python
Arguments: C:\path\to\battery_automation.py run
Trigger: Daily at 13:00
```

**macOS/Linux Cron:**
```bash
0 13 * * * cd /path/to/Utilities && python3 battery_automation.py run
```

ESP32 runs 24/7, PC only needed once daily for optimization!

## 🔍 Troubleshooting

### WiFi Connection Issues

**Problem:** ESP32 won't connect to WiFi

**Solutions:**
- Check SSID and password (case-sensitive!)
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router
- Check if MAC filtering is enabled on router

**Debug:**
```cpp
Serial.println(WiFi.status());
// WL_CONNECTED = 3
// WL_NO_SSID_AVAIL = 1
// WL_CONNECT_FAILED = 4
```

### Modbus Communication Fails

**Problem:** Cannot read battery status

**Solutions:**
1. **Check wiring:**
   - Verify A-A, B-B connections
   - Check for loose connections
   - Ensure common ground

2. **Check Modbus settings:**
   - Verify slave ID (usually 1)
   - Check baudrate (usually 9600)
   - Try swapping A and B wires

3. **Check register addresses:**
   - Addresses vary by Growatt model
   - Consult your inverter's Modbus manual
   - Common SPH registers: SOC=1014, Voltage=1013, Power=1009

4. **Enable Modbus on Growatt:**
   - Some models need Modbus enabled in settings
   - Check Growatt app: Settings → Communication

**Debug Modbus:**
```cpp
uint8_t result = growatt.readHoldingRegisters(1014, 1);
Serial.print("Modbus result: ");
Serial.println(result, HEX);
// ku8MBSuccess = 0x00
// ku8MBIllegalFunction = 0x01
// ku8MBIllegalDataAddress = 0x02
```

### ESP32 Reboots Randomly

**Problem:** ESP32 keeps resetting

**Solutions:**
- **Power supply:** Use quality 5V 1A+ adapter
- **Decoupling capacitor:** Add 100µF cap between 3.3V and GND
- **Brown-out:** Increase brown-out voltage in code
- **Watchdog:** Add `delay()` in tight loops

### Schedule Not Applied

**Problem:** Schedule sent but not active on Growatt

**Solutions:**
1. Check Modbus write succeeded
2. Verify register addresses for your model
3. Check Growatt doesn't override from app
4. Some models need a "write enable" command first
5. Try power cycling the Growatt

## 🎓 Advanced Features

### Add Manual Controls

**Edit the sketch to add buttons:**

```cpp
// Add button to force charge NOW
const int FORCE_CHARGE_PIN = 5;

void setup() {
  pinMode(FORCE_CHARGE_PIN, INPUT_PULLUP);
}

void loop() {
  if (digitalRead(FORCE_CHARGE_PIN) == LOW) {
    // Force charge
    setChargeMode(true);
    delay(1000);
  }
}
```

### Add OLED Display

Show status on a small screen:

```cpp
#include <Wire.h>
#include <Adafruit_SSD1306.h>

Adafruit_SSD1306 display(128, 64, &Wire, -1);

void displayStatus() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.printf("SOC: %.1f%%\n", batteryStatus.soc);
  display.printf("Power: %.0fW\n", batteryStatus.power);
  display.display();
}
```

### OTA Updates

Enable over-the-air firmware updates:

```cpp
#include <ArduinoOTA.h>

void setup() {
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
}
```

Then update wirelessly:
```bash
# In Arduino IDE:
# Tools → Port → ESP32 at 192.168.1.50
# Upload as normal!
```

### MQTT Integration

Send data to Home Assistant:

```cpp
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient mqtt(espClient);

void publishStatus() {
  mqtt.publish("battery/soc", String(batteryStatus.soc).c_str());
  mqtt.publish("battery/power", String(batteryStatus.power).c_str());
}
```

## 📊 Monitoring & Logs

### View Real-Time Logs

**Serial Monitor:**
```
Tools → Serial Monitor → 115200 baud
```

### Remote Logging

Add remote syslog:

```cpp
#include <Syslog.h>

Syslog syslog(udpClient, "192.168.1.100", 514, "ESP32", "BatteryController");

void setup() {
  syslog.log(LOG_INFO, "ESP32 started");
}
```

### Save Logs to SD Card

```cpp
#include <SD.h>

void logToSD(String message) {
  File logFile = SD.open("/battery.log", FILE_APPEND);
  logFile.println(message);
  logFile.close();
}
```

## 🔒 Security Considerations

### Add Authentication

```cpp
// Simple authentication
const char* API_KEY = "your_secret_key";

void handlePostSchedule() {
  if (!server.hasHeader("X-API-Key") ||
      server.header("X-API-Key") != API_KEY) {
    server.send(401, "text/plain", "Unauthorized");
    return;
  }
  // Process request...
}
```

### Use HTTPS

For production, consider using:
- ESP32 HTTPS server
- Reverse proxy (nginx) with SSL
- VPN for remote access

## 💾 Data Persistence

ESP32 saves schedule to flash memory, survives power loss!

**Manual backup:**
```cpp
void backupSchedule() {
  File file = SPIFFS.open("/schedule_backup.json", "w");
  // Write schedule JSON
  file.close();
}
```

## 🎯 Performance Tips

### Reduce Power Consumption

```cpp
// Enable WiFi sleep
WiFi.setSleep(true);

// Lower CPU frequency
setCpuFrequencyMhz(80); // From 240MHz to 80MHz
```

### Optimize Modbus Timing

```cpp
// Reduce delays between reads
delay(50);  // Instead of 100ms

// Batch read registers
growatt.readHoldingRegisters(1009, 10); // Read 10 at once
```

## 📚 Additional Resources

- **ESP32 Datasheet:** https://www.espressif.com/en/products/socs/esp32
- **Modbus Protocol:** https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
- **Growatt Modbus Manual:** Check your inverter model documentation
- **Arduino ESP32 Core:** https://docs.espressif.com/projects/arduino-esp32/

## 🆘 Getting Help

**If you're stuck:**

1. Check Serial Monitor output
2. Test each component separately:
   - WiFi connection
   - Modbus communication
   - Web server
3. Use a Modbus scanner tool to verify inverter
4. Check Growatt forums for your specific model
5. Try the dry-run mode first

## ✅ Success Checklist

- [ ] ESP32 powers on and connects to WiFi
- [ ] Can access web interface at ESP32's IP
- [ ] Modbus reads battery SOC correctly
- [ ] Can upload test schedule via API
- [ ] Schedule appears in Growatt app/display
- [ ] Battery charges during scheduled times
- [ ] Python automation sends schedules successfully
- [ ] System runs for 24+ hours without issues

## 🎉 You're Done!

Your ESP32 is now a smart battery controller running 24/7 for less than €20!

**Next steps:**
1. Monitor for a week to ensure stability
2. Fine-tune Modbus register addresses for your model
3. Add custom features (display, buttons, etc.)
4. Enjoy automatic optimal charging every day!

---

**Cost Comparison:**

| Solution | Hardware Cost | Power Usage | Complexity |
|----------|--------------|-------------|------------|
| ESP32 (this guide) | €15-30 | ~1W | ⭐⭐ Medium |
| Raspberry Pi | €40-80 | ~3W | ⭐⭐⭐ High |
| PC 24/7 | €300+ | ~50W | ⭐ Easy |
| Growatt Cloud | €0 | 0W | ⭐ Easy |

**Recommendation:** ESP32 offers the best balance of cost, reliability, and local control!
