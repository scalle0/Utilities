/*
 * Growatt Battery Controller for ESP32
 *
 * This sketch turns your ESP32 into a smart battery controller that:
 * - Receives optimized charging schedules via WiFi/HTTP
 * - Controls Growatt inverter via Modbus RTU (RS485)
 * - Executes time-based charging schedules
 * - Provides web interface for monitoring
 *
 * Hardware Required:
 * - ESP32 Dev Board (ESP32-WROOM-32 or similar)
 * - RS485 to TTL Module (MAX485 or similar)
 * - Connections:
 *   - ESP32 RX2 (GPIO16) -> RS485 RO
 *   - ESP32 TX2 (GPIO17) -> RS485 DI
 *   - ESP32 GPIO4 -> RS485 DE+RE (tied together)
 *   - RS485 A -> Growatt A
 *   - RS485 B -> Growatt B
 *   - Common GND
 *
 * Author: Battery Automation System
 * Version: 1.0
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ModbusMaster.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <time.h>

// ============================================================================
// CONFIGURATION - Edit these for your setup
// ============================================================================

// WiFi credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Modbus configuration
#define MODBUS_SERIAL Serial2        // Use Serial2 for Modbus
#define RS485_RX 16                  // ESP32 RX2 pin
#define RS485_TX 17                  // ESP32 TX2 pin
#define RS485_DE_RE 4                // DE and RE pins (tied together)
#define MODBUS_SLAVE_ID 1            // Growatt Modbus slave ID
#define MODBUS_BAUDRATE 9600

// Time configuration
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = 3600;    // Adjust for your timezone (3600 = GMT+1)
const int DAYLIGHT_OFFSET_SEC = 3600; // Adjust for DST

// Web server
WebServer server(80);

// Modbus
ModbusMaster growatt;

// Preferences for persistent storage
Preferences preferences;

// ============================================================================
// DATA STRUCTURES
// ============================================================================

#define MAX_TIME_SLOTS 6

struct TimeSlot {
  bool enabled;
  uint8_t startHour;
  uint8_t startMinute;
  uint8_t endHour;
  uint8_t endMinute;
  uint8_t powerPercent;
};

struct Schedule {
  TimeSlot slots[MAX_TIME_SLOTS];
  uint8_t numSlots;
  time_t lastUpdate;
  bool isValid;
};

Schedule currentSchedule;

// Battery status
struct BatteryStatus {
  float soc;           // State of charge (%)
  float voltage;       // Voltage (V)
  float current;       // Current (A)
  float power;         // Power (W)
  bool isCharging;
  time_t lastRead;
};

BatteryStatus batteryStatus;

// ============================================================================
// MODBUS FUNCTIONS
// ============================================================================

// Modbus pre-transmission callback
void preTransmission() {
  digitalWrite(RS485_DE_RE, HIGH);
}

// Modbus post-transmission callback
void postTransmission() {
  digitalWrite(RS485_DE_RE, LOW);
}

// Initialize Modbus
void initModbus() {
  Serial.println("Initializing Modbus...");

  pinMode(RS485_DE_RE, OUTPUT);
  digitalWrite(RS485_DE_RE, LOW);

  MODBUS_SERIAL.begin(MODBUS_BAUDRATE, SERIAL_8N1, RS485_RX, RS485_TX);

  growatt.begin(MODBUS_SLAVE_ID, MODBUS_SERIAL);
  growatt.preTransmission(preTransmission);
  growatt.postTransmission(postTransmission);

  Serial.println("✓ Modbus initialized");
}

// Read battery status from Growatt
bool readBatteryStatus() {
  uint8_t result;
  uint16_t data[10];

  // Read holding registers (addresses may vary by model - check your documentation)
  // Example addresses for SPH series:
  const uint16_t SOC_REGISTER = 1014;
  const uint16_t BATTERY_VOLTAGE_REGISTER = 1013;
  const uint16_t BATTERY_POWER_REGISTER = 1009;

  // Read SOC
  result = growatt.readHoldingRegisters(SOC_REGISTER, 1);
  if (result == growatt.ku8MBSuccess) {
    batteryStatus.soc = growatt.getResponseBuffer(0);
  } else {
    Serial.println("✗ Failed to read battery SOC");
    return false;
  }

  delay(100);

  // Read voltage
  result = growatt.readHoldingRegisters(BATTERY_VOLTAGE_REGISTER, 1);
  if (result == growatt.ku8MBSuccess) {
    batteryStatus.voltage = growatt.getResponseBuffer(0) / 10.0;
  }

  delay(100);

  // Read power
  result = growatt.readHoldingRegisters(BATTERY_POWER_REGISTER, 1);
  if (result == growatt.ku8MBSuccess) {
    int16_t power = growatt.getResponseBuffer(0);
    batteryStatus.power = power;
    batteryStatus.isCharging = (power > 0);
  }

  batteryStatus.lastRead = time(nullptr);
  return true;
}

// Write time slot to Growatt
bool writeTimeSlot(uint8_t slotNumber, const TimeSlot& slot) {
  uint8_t result;

  // Base register for time slots (example - verify for your model)
  // Typically: Slot 1 = 1090-1095, Slot 2 = 1096-1101, etc.
  const uint16_t BASE_REGISTER = 1090;
  uint16_t slotOffset = (slotNumber - 1) * 6;

  Serial.printf("Writing time slot %d: %02d:%02d-%02d:%02d\n",
                slotNumber, slot.startHour, slot.startMinute,
                slot.endHour, slot.endMinute);

  // Write start hour
  result = growatt.writeSingleRegister(BASE_REGISTER + slotOffset, slot.startHour);
  if (result != growatt.ku8MBSuccess) {
    Serial.println("✗ Failed to write start hour");
    return false;
  }
  delay(100);

  // Write start minute
  result = growatt.writeSingleRegister(BASE_REGISTER + slotOffset + 1, slot.startMinute);
  if (result != growatt.ku8MBSuccess) return false;
  delay(100);

  // Write end hour
  result = growatt.writeSingleRegister(BASE_REGISTER + slotOffset + 2, slot.endHour);
  if (result != growatt.ku8MBSuccess) return false;
  delay(100);

  // Write end minute
  result = growatt.writeSingleRegister(BASE_REGISTER + slotOffset + 3, slot.endMinute);
  if (result != growatt.ku8MBSuccess) return false;
  delay(100);

  // Write power percentage (usually 100%)
  result = growatt.writeSingleRegister(BASE_REGISTER + slotOffset + 4, slot.powerPercent);
  if (result != growatt.ku8MBSuccess) return false;
  delay(100);

  // Enable/disable slot
  result = growatt.writeSingleRegister(BASE_REGISTER + slotOffset + 5, slot.enabled ? 1 : 0);
  if (result != growatt.ku8MBSuccess) {
    Serial.println("✗ Failed to enable slot");
    return false;
  }

  Serial.println("✓ Time slot written successfully");
  return true;
}

// Apply entire schedule to Growatt
bool applySchedule(const Schedule& schedule) {
  Serial.println("\n=== Applying Schedule to Growatt ===");

  for (uint8_t i = 0; i < MAX_TIME_SLOTS; i++) {
    if (i < schedule.numSlots) {
      if (!writeTimeSlot(i + 1, schedule.slots[i])) {
        Serial.printf("✗ Failed to write slot %d\n", i + 1);
        return false;
      }
    } else {
      // Disable unused slots
      TimeSlot emptySlot = {false, 0, 0, 0, 0, 100};
      writeTimeSlot(i + 1, emptySlot);
    }
    delay(200);
  }

  Serial.println("✓ Schedule applied successfully\n");
  return true;
}

// ============================================================================
// SCHEDULE MANAGEMENT
// ============================================================================

// Save schedule to persistent storage
void saveSchedule() {
  preferences.begin("battery", false);
  preferences.putBytes("schedule", &currentSchedule, sizeof(Schedule));
  preferences.end();
  Serial.println("✓ Schedule saved to flash");
}

// Load schedule from persistent storage
void loadSchedule() {
  preferences.begin("battery", true);
  size_t len = preferences.getBytesLength("schedule");
  if (len == sizeof(Schedule)) {
    preferences.getBytes("schedule", &currentSchedule, sizeof(Schedule));
    Serial.println("✓ Schedule loaded from flash");
  } else {
    Serial.println("! No saved schedule found");
    currentSchedule.isValid = false;
  }
  preferences.end();
}

// ============================================================================
// WEB SERVER HANDLERS
// ============================================================================

// Root page - shows status and controls
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>Growatt Battery Controller</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="10">
  <style>
    body { font-family: Arial; margin: 20px; background: #f0f0f0; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
    h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
    .status { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .schedule { background: #fff3e0; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .slot { background: #f5f5f5; padding: 10px; margin: 5px 0; border-left: 4px solid #4CAF50; }
    .value { font-weight: bold; color: #4CAF50; }
    .timestamp { color: #666; font-size: 0.9em; }
    button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    button:hover { background: #45a049; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔋 Growatt Battery Controller</h1>

    <div class="status">
      <h2>Battery Status</h2>
      <p>State of Charge: <span class="value">)rawliteral" + String(batteryStatus.soc, 1) + R"rawliteral(%</span></p>
      <p>Voltage: <span class="value">)rawliteral" + String(batteryStatus.voltage, 1) + R"rawliteral( V</span></p>
      <p>Power: <span class="value">)rawliteral" + String(batteryStatus.power, 0) + R"rawliteral( W</span>
         )rawliteral" + String(batteryStatus.isCharging ? "⚡ Charging" : "🔋 Discharging") + R"rawliteral(</p>
      <p class="timestamp">Last update: )rawliteral" + String(ctime(&batteryStatus.lastRead)) + R"rawliteral(</p>
    </div>

    <div class="schedule">
      <h2>Charging Schedule</h2>
      )rawliteral";

  if (currentSchedule.isValid && currentSchedule.numSlots > 0) {
    for (uint8_t i = 0; i < currentSchedule.numSlots; i++) {
      TimeSlot slot = currentSchedule.slots[i];
      if (slot.enabled) {
        html += "<div class='slot'>";
        html += "Slot " + String(i + 1) + ": ";
        html += String(slot.startHour) + ":" + (slot.startMinute < 10 ? "0" : "") + String(slot.startMinute);
        html += " - ";
        html += String(slot.endHour) + ":" + (slot.endMinute < 10 ? "0" : "") + String(slot.endMinute);
        html += " @ " + String(slot.powerPercent) + "%";
        html += "</div>";
      }
    }
    html += "<p class='timestamp'>Last update: " + String(ctime(&currentSchedule.lastUpdate)) + "</p>";
  } else {
    html += "<p>No schedule loaded</p>";
  }

  html += R"rawliteral(
    </div>

    <div style="margin-top: 20px;">
      <button onclick="location.reload()">🔄 Refresh</button>
      <button onclick="fetch('/api/refresh')">📡 Fetch New Schedule</button>
      <button onclick="fetch('/api/status')">📊 Update Status</button>
    </div>

    <div style="margin-top: 20px; padding: 10px; background: #e3f2fd; border-radius: 5px;">
      <h3>API Endpoints</h3>
      <p><code>POST /api/schedule</code> - Upload new schedule (JSON)</p>
      <p><code>GET /api/status</code> - Get battery status (JSON)</p>
      <p><code>GET /api/schedule</code> - Get current schedule (JSON)</p>
    </div>
  </div>
</body>
</html>
)rawliteral";

  server.send(200, "text/html", html);
}

// API: Get battery status
void handleGetStatus() {
  readBatteryStatus();

  StaticJsonDocument<512> doc;
  doc["soc"] = batteryStatus.soc;
  doc["voltage"] = batteryStatus.voltage;
  doc["power"] = batteryStatus.power;
  doc["current"] = batteryStatus.current;
  doc["is_charging"] = batteryStatus.isCharging;
  doc["timestamp"] = batteryStatus.lastRead;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// API: Get current schedule
void handleGetSchedule() {
  StaticJsonDocument<1024> doc;

  JsonArray slots = doc.createNestedArray("slots");
  for (uint8_t i = 0; i < currentSchedule.numSlots; i++) {
    if (currentSchedule.slots[i].enabled) {
      JsonObject slot = slots.createNestedObject();
      slot["enabled"] = currentSchedule.slots[i].enabled;
      slot["start_hour"] = currentSchedule.slots[i].startHour;
      slot["start_minute"] = currentSchedule.slots[i].startMinute;
      slot["end_hour"] = currentSchedule.slots[i].endHour;
      slot["end_minute"] = currentSchedule.slots[i].endMinute;
      slot["power_percent"] = currentSchedule.slots[i].powerPercent;
    }
  }

  doc["num_slots"] = currentSchedule.numSlots;
  doc["last_update"] = currentSchedule.lastUpdate;
  doc["is_valid"] = currentSchedule.isValid;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// API: Receive new schedule
void handlePostSchedule() {
  if (server.hasArg("plain") == false) {
    server.send(400, "text/plain", "Body not received");
    return;
  }

  String body = server.arg("plain");
  Serial.println("Received schedule:");
  Serial.println(body);

  StaticJsonDocument<2048> doc;
  DeserializationError error = deserializeJson(doc, body);

  if (error) {
    Serial.print("JSON parsing failed: ");
    Serial.println(error.c_str());
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  // Parse schedule
  Schedule newSchedule;
  newSchedule.numSlots = 0;
  newSchedule.lastUpdate = time(nullptr);
  newSchedule.isValid = true;

  JsonArray slots = doc["charging_windows"];
  for (JsonObject slot : slots) {
    if (newSchedule.numSlots >= MAX_TIME_SLOTS) break;

    TimeSlot ts;
    ts.enabled = true;
    ts.startHour = slot["start_hour"];
    ts.startMinute = slot["start_minute"];
    ts.endHour = slot["end_hour"];
    ts.endMinute = slot["end_minute"];
    ts.powerPercent = 100;

    newSchedule.slots[newSchedule.numSlots++] = ts;
  }

  // Apply to Growatt
  if (applySchedule(newSchedule)) {
    currentSchedule = newSchedule;
    saveSchedule();
    server.send(200, "text/plain", "Schedule applied successfully");
  } else {
    server.send(500, "text/plain", "Failed to apply schedule");
  }
}

// ============================================================================
// SETUP & LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=== Growatt Battery Controller ===");
  Serial.println("Version 1.0");

  // Connect to WiFi
  Serial.printf("Connecting to WiFi: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ WiFi connection failed");
  }

  // Initialize NTP
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
  Serial.println("✓ NTP configured");

  // Initialize Modbus
  initModbus();

  // Load saved schedule
  loadSchedule();

  // Setup web server
  server.on("/", handleRoot);
  server.on("/api/status", HTTP_GET, handleGetStatus);
  server.on("/api/schedule", HTTP_GET, handleGetSchedule);
  server.on("/api/schedule", HTTP_POST, handlePostSchedule);

  server.begin();
  Serial.println("✓ Web server started");

  Serial.println("\n=== Initialization Complete ===");
  Serial.printf("Access web interface at: http://%s\n\n", WiFi.localIP().toString().c_str());
}

void loop() {
  // Handle web requests
  server.handleClient();

  // Update battery status every 30 seconds
  static unsigned long lastStatusUpdate = 0;
  if (millis() - lastStatusUpdate > 30000) {
    readBatteryStatus();
    lastStatusUpdate = millis();
  }

  delay(10);
}
