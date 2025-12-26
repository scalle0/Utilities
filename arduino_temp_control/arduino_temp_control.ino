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
  - Automatic heater control with adjustable thresholds (18-25°C)
  - IoT Cloud dashboard control to enable/disable automation
  - Manual override with Modulino button
  - Adjustable temperature thresholds from dashboard
*/

#include "thingProperties.h"
#include <Modulino.h>

// Modulino objects
ModulinoThermo thermo;
ModulinoButtons buttons;

// Temperature thresholds are now cloud variables (defined in thingProperties.h)
// tempThresholdLow: Turn heater ON when temp drops below this
// tempThresholdHigh: Turn heater OFF when temp rises above this
// Range: 18.0 to 25.0°C

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
  tempThresholdLow = 23.0;     // Default: Turn ON below 23°C
  tempThresholdHigh = 24.0;    // Default: Turn OFF above 24°C

  Serial.println("Setup complete!");
  Serial.print("Temperature thresholds: ");
  Serial.print(tempThresholdLow);
  Serial.print("°C - ");
  Serial.print(tempThresholdHigh);
  Serial.println("°C");
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
  if (currentTemperature < tempThresholdLow && !heaterState) {
    // Temperature too low, turn heater ON
    shouldBeOn = true;
    heaterState = true;
    heaterStatus = true;
    Serial.print("Temperature below ");
    Serial.print(tempThresholdLow);
    Serial.println("°C - Heater should be ON");
  }
  else if (currentTemperature > tempThresholdHigh && heaterState) {
    // Temperature high enough, turn heater OFF
    shouldBeOn = false;
    heaterState = false;
    heaterStatus = false;
    Serial.print("Temperature above ");
    Serial.print(tempThresholdHigh);
    Serial.println("°C - Heater should be OFF");
  }

  // Note: Actual Google Home control happens via IoT Cloud trigger
  // The heaterStatus variable will be monitored by Arduino IoT Cloud triggers
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
    Serial.println(tempThresholdLow);
  }

  Serial.print("Lower temperature threshold set to: ");
  Serial.print(tempThresholdLow);
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
    Serial.println(tempThresholdHigh);
  }

  Serial.print("Upper temperature threshold set to: ");
  Serial.print(tempThresholdHigh);
  Serial.println("°C");
}
