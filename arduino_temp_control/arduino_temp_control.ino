/*
  Arduino R4 WiFi Temperature Control with Modulino

  IMPORTANT SETUP NOTE:
  Before uploading, you must create thingProperties.h from the template:
  1. Copy thingProperties_template.h to thingProperties.h
  2. Edit thingProperties.h with your WiFi and Arduino IoT Cloud credentials
  3. See README.md for detailed setup instructions

  This sketch monitors temperature using Modulino Thermo and controls
  a heater through Google Home based on temperature thresholds.

  Hardware:
  - Arduino R4 WiFi
  - Modulino Thermo (for temperature sensing)
  - Modulino Buttons (for manual override)

  Features:
  - Temperature monitoring
  - Automatic heater control (below 23°C ON, above 24°C OFF)
  - IoT Cloud dashboard control to enable/disable automation
  - Manual override with Modulino button
*/

#include "thingProperties.h"
#include <Modulino.h>

// Modulino objects
ModulinoThermo thermo;
ModulinoButtons buttons;

// Temperature thresholds
const float TEMP_THRESHOLD_LOW = 23.0;   // Turn heater ON below this
const float TEMP_THRESHOLD_HIGH = 24.0;  // Turn heater OFF above this

// Timing variables
unsigned long lastTempRead = 0;
const unsigned long TEMP_READ_INTERVAL = 5000;  // Read temp every 5 seconds

// Button state tracking
bool lastButtonState = false;

void setup() {
  Serial.begin(9600);
  delay(1500);

  Serial.println("Arduino R4 WiFi Temperature Control Starting...");

  // Initialize Modulino communication
  Modulino.begin();

  // Initialize Modulino devices
  thermo.begin();
  buttons.begin();

  Serial.println("Modulino devices initialized");

  // Initialize Arduino IoT Cloud
  initProperties();
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);

  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();

  // Initialize cloud variables
  autoControlEnabled = true;   // Start with automation enabled
  heaterStatus = false;        // Heater starts OFF
  currentTemperature = 0.0;

  Serial.println("Setup complete!");
}

void loop() {
  // Update IoT Cloud connection
  ArduinoCloud.update();

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

  delay(100);
}

void readTemperature() {
  // Read temperature from Modulino Thermo
  float temp = thermo.getTemperature();

  if (!isnan(temp)) {
    currentTemperature = temp;
    Serial.print("Temperature: ");
    Serial.print(currentTemperature);
    Serial.println(" °C");
  } else {
    Serial.println("Error reading temperature!");
  }
}

void controlHeater() {
  static bool heaterState = false;
  bool shouldBeOn = false;

  // Hysteresis control to prevent rapid switching
  if (currentTemperature < TEMP_THRESHOLD_LOW && !heaterState) {
    // Temperature too low, turn heater ON
    shouldBeOn = true;
    heaterState = true;
    heaterStatus = true;
    Serial.println("Temperature below threshold - Heater should be ON");
  }
  else if (currentTemperature > TEMP_THRESHOLD_HIGH && heaterState) {
    // Temperature high enough, turn heater OFF
    shouldBeOn = false;
    heaterState = false;
    heaterStatus = false;
    Serial.println("Temperature above threshold - Heater should be OFF");
  }

  // Note: Actual Google Home control happens via IoT Cloud trigger
  // The heaterStatus variable will be monitored by IFTTT or Arduino IoT Cloud triggers
}

void checkButton() {
  // Check if button A is pressed for manual override
  if (buttons.update()) {
    bool buttonA = buttons.isPressed(0);  // Button A

    if (buttonA && !lastButtonState) {
      // Button just pressed - toggle automation
      autoControlEnabled = !autoControlEnabled;
      Serial.print("Automation ");
      Serial.println(autoControlEnabled ? "ENABLED" : "DISABLED");
    }

    lastButtonState = buttonA;
  }
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
