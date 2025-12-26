/*
  ESP32 Temperature Control with Arduino IoT Cloud

  IMPORTANT SETUP NOTE:
  Before uploading, you must create thingProperties.h from the template:
  1. Copy thingProperties_template.h to thingProperties.h
  2. Edit thingProperties.h with your WiFi and Arduino IoT Cloud credentials
  3. See README.md for detailed setup instructions

  This sketch monitors temperature and controls a heater through Google Home
  based on adjustable temperature thresholds.

  Hardware:
  - ESP32 Development Board (any variant)
  - DS18B20 temperature sensor (recommended) OR DHT22
  - Push buttons (for manual override)
  - Smart plug compatible with Google Home

  Features:
  - Temperature monitoring
  - Automatic heater control with adjustable thresholds (18-25°C)
  - IoT Cloud dashboard control to enable/disable automation
  - Manual override with physical button
  - Adjustable temperature thresholds from dashboard
*/

#include "thingProperties.h"

// ===== SENSOR SELECTION =====
// Uncomment ONE of the following lines to choose your sensor:
#define USE_DS18B20    // DS18B20 1-Wire digital temperature sensor (recommended)
//#define USE_DHT22      // DHT22 temperature & humidity sensor

// ===== SENSOR LIBRARIES =====
#ifdef USE_DS18B20
  #include <OneWire.h>
  #include <DallasTemperature.h>
#endif

#ifdef USE_DHT22
  #include <DHT.h>
#endif

// ===== PIN DEFINITIONS =====
// Adjust these pins based on your wiring
#ifdef USE_DS18B20
  #define TEMP_SENSOR_PIN 4      // GPIO4 for DS18B20 data line
#endif

#ifdef USE_DHT22
  #define TEMP_SENSOR_PIN 4      // GPIO4 for DHT22 data line
  #define DHT_TYPE DHT22
#endif

#define BUTTON_PIN 5             // GPIO5 for automation toggle button
#define LED_PIN 2                // GPIO2 (built-in LED) for status indication

// ===== SENSOR OBJECTS =====
#ifdef USE_DS18B20
  OneWire oneWire(TEMP_SENSOR_PIN);
  DallasTemperature sensors(&oneWire);
#endif

#ifdef USE_DHT22
  DHT dht(TEMP_SENSOR_PIN, DHT_TYPE);
#endif

// ===== TIMING VARIABLES =====
unsigned long lastTempRead = 0;
const unsigned long TEMP_READ_INTERVAL = 5000;  // Read temp every 5 seconds

// ===== BUTTON VARIABLES =====
bool lastButtonState = HIGH;  // Button not pressed (pull-up)
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 50;

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println("ESP32 Temperature Control Starting...");
  Serial.print("Chip Model: ");
  Serial.println(ESP.getChipModel());
  Serial.print("Chip Revision: ");
  Serial.println(ESP.getChipRevision());
  Serial.print("Flash Size: ");
  Serial.println(ESP.getFlashChipSize());

  // Initialize GPIO pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Button with internal pull-up
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Initialize temperature sensor
  #ifdef USE_DS18B20
    sensors.begin();
    int deviceCount = sensors.getDeviceCount();
    Serial.print("Found ");
    Serial.print(deviceCount);
    Serial.println(" DS18B20 sensor(s)");
    if (deviceCount == 0) {
      Serial.println("ERROR: No DS18B20 sensors found! Check wiring.");
    }
    sensors.setResolution(12);  // 12-bit resolution (0.0625°C precision)
  #endif

  #ifdef USE_DHT22
    dht.begin();
    Serial.println("DHT22 sensor initialized");
  #endif

  // Initialize Arduino IoT Cloud
  Serial.println("Connecting to Arduino IoT Cloud...");
  initProperties();
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);

  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();

  // Initialize cloud variables
  autoControlEnabled = true;      // Start with automation enabled
  heaterStatus = false;           // Heater starts OFF
  currentTemperature = 0.0;
  tempThresholdLow = 23.0;        // Default: Turn ON below 23°C
  tempThresholdHigh = 24.0;       // Default: Turn OFF above 24°C

  Serial.println("Setup complete!");
  Serial.print("Temperature thresholds: ");
  Serial.print(tempThresholdLow);
  Serial.print("°C - ");
  Serial.print(tempThresholdHigh);
  Serial.println("°C");

  // Blink LED to indicate ready
  for(int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}

void loop() {
  // Update IoT Cloud connection
  ArduinoCloud.update();

  // Update LED based on heater status
  digitalWrite(LED_PIN, heaterStatus ? HIGH : LOW);

  // Read temperature periodically
  if (millis() - lastTempRead >= TEMP_READ_INTERVAL) {
    readTemperature();
    lastTempRead = millis();
  }

  // Check button for manual override
  checkButton();

  // Control heater based on temperature (if automation enabled)
  if (autoControlEnabled) {
    controlHeater();
  }

  delay(10);  // Small delay for stability
}

void readTemperature() {
  float temp = NAN;

  #ifdef USE_DS18B20
    sensors.requestTemperatures();  // Request temperature reading
    temp = sensors.getTempCByIndex(0);  // Get temperature in Celsius

    if (temp == DEVICE_DISCONNECTED_C || temp == 85.0) {
      // 85.0 is error value, DEVICE_DISCONNECTED_C is -127.0
      Serial.println("Error reading DS18B20 sensor!");
      temp = NAN;
    }
  #endif

  #ifdef USE_DHT22
    temp = dht.readTemperature();  // Read temperature in Celsius

    if (isnan(temp)) {
      Serial.println("Error reading DHT22 sensor!");
    }
  #endif

  if (!isnan(temp)) {
    currentTemperature = temp;
    Serial.print("Temperature: ");
    Serial.print(currentTemperature, 1);  // Print with 1 decimal place
    Serial.println(" °C");
  } else {
    Serial.println("Error: Invalid temperature reading!");
  }
}

void controlHeater() {
  static bool heaterState = false;

  // Hysteresis control to prevent rapid switching
  if (currentTemperature < tempThresholdLow && !heaterState) {
    // Temperature too low, turn heater ON
    heaterState = true;
    heaterStatus = true;
    Serial.print("Temperature below ");
    Serial.print(tempThresholdLow, 1);
    Serial.println("°C - Heater should be ON");
  }
  else if (currentTemperature > tempThresholdHigh && heaterState) {
    // Temperature high enough, turn heater OFF
    heaterState = false;
    heaterStatus = false;
    Serial.print("Temperature above ");
    Serial.print(tempThresholdHigh, 1);
    Serial.println("°C - Heater should be OFF");
  }

  // Note: Actual Google Home control happens via IoT Cloud trigger
  // The heaterStatus variable will be monitored by Arduino IoT Cloud triggers
}

void checkButton() {
  // Read button state with debouncing
  bool buttonState = digitalRead(BUTTON_PIN);

  // Check if button state changed
  if (buttonState != lastButtonState) {
    lastDebounceTime = millis();
  }

  // If button state has been stable for debounce period
  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    // Button pressed (LOW due to pull-up) and was previously not pressed
    if (buttonState == LOW && lastButtonState == HIGH) {
      // Toggle automation
      autoControlEnabled = !autoControlEnabled;
      Serial.print("Button pressed - Automation ");
      Serial.println(autoControlEnabled ? "ENABLED" : "DISABLED");

      // Blink LED to confirm button press
      for(int i = 0; i < 2; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
        delay(100);
      }
    }
  }

  lastButtonState = buttonState;
}

/*
  Cloud variable callback functions
  These are called when variables change in the IoT Cloud dashboard
*/

void onAutoControlEnabledChange() {
  Serial.print("Auto control changed to: ");
  Serial.println(autoControlEnabled ? "ENABLED" : "DISABLED");

  if (!autoControlEnabled) {
    // When disabled, turn off heater for safety
    heaterStatus = false;
    Serial.println("Automation disabled - Heater turned OFF");
  }
}

void onManualHeaterControlChange() {
  // Allow manual control from dashboard when automation is disabled
  if (!autoControlEnabled) {
    heaterStatus = manualHeaterControl;
    Serial.print("Manual heater control: ");
    Serial.println(heaterStatus ? "ON" : "OFF");
  }
}

void onTempThresholdLowChange() {
  // Validate and constrain lower threshold
  // Range: 18.0 to 25.0°C
  // Must be less than upper threshold

  if (tempThresholdLow < 18.0) {
    tempThresholdLow = 18.0;
    Serial.println("Warning: Lower threshold set to minimum (18.0°C)");
  }
  else if (tempThresholdLow > 25.0) {
    tempThresholdLow = 25.0;
    Serial.println("Warning: Lower threshold set to maximum (25.0°C)");
  }

  // Ensure hysteresis: low must be less than high
  if (tempThresholdLow >= tempThresholdHigh) {
    tempThresholdLow = tempThresholdHigh - 0.5;
    Serial.print("Warning: Lower threshold adjusted to maintain hysteresis: ");
    Serial.println(tempThresholdLow, 1);
  }

  Serial.print("Lower temperature threshold set to: ");
  Serial.print(tempThresholdLow, 1);
  Serial.println("°C");
}

void onTempThresholdHighChange() {
  // Validate and constrain upper threshold
  // Range: 18.0 to 25.0°C
  // Must be greater than lower threshold

  if (tempThresholdHigh < 18.0) {
    tempThresholdHigh = 18.0;
    Serial.println("Warning: Upper threshold set to minimum (18.0°C)");
  }
  else if (tempThresholdHigh > 25.0) {
    tempThresholdHigh = 25.0;
    Serial.println("Warning: Upper threshold set to maximum (25.0°C)");
  }

  // Ensure hysteresis: high must be greater than low
  if (tempThresholdHigh <= tempThresholdLow) {
    tempThresholdHigh = tempThresholdLow + 0.5;
    Serial.print("Warning: Upper threshold adjusted to maintain hysteresis: ");
    Serial.println(tempThresholdHigh, 1);
  }

  Serial.print("Upper temperature threshold set to: ");
  Serial.print(tempThresholdHigh, 1);
  Serial.println("°C");
}
