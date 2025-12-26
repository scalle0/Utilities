/*
  Configuration Template

  Copy this file's contents to customize settings without modifying main code.
  Alternatively, modify values directly in arduino_temp_control.ino
*/

#ifndef CONFIG_H
#define CONFIG_H

// ============================================
// TEMPERATURE THRESHOLDS
// ============================================

// Temperature below which heater turns ON (Celsius)
#define TEMP_THRESHOLD_LOW 23.0

// Temperature above which heater turns OFF (Celsius)
#define TEMP_THRESHOLD_HIGH 24.0

// Hysteresis band: TEMP_THRESHOLD_HIGH - TEMP_THRESHOLD_LOW
// Recommended: 1-2°C to prevent rapid cycling
// Example: 23-24°C = 1°C hysteresis


// ============================================
// TIMING SETTINGS
// ============================================

// How often to read temperature (milliseconds)
// Default: 5000 (5 seconds)
// Range: 1000-60000 (1 second to 1 minute)
#define TEMP_READ_INTERVAL 5000

// Cloud update interval (handled by ArduinoIoTCloud library)
// Typically 1-5 seconds for value changes


// ============================================
// SAFETY SETTINGS
// ============================================

// Maximum allowed temperature (safety shutoff)
// If temperature exceeds this, disable heater regardless of auto mode
#define MAX_SAFE_TEMPERATURE 30.0

// Minimum allowed temperature (sensor check)
// If temperature is below this, sensor may be faulty
#define MIN_VALID_TEMPERATURE -10.0

// Enable safety shutoff feature
#define ENABLE_SAFETY_SHUTOFF true


// ============================================
// MODULINO SETTINGS
// ============================================

// Modulino button index for automation toggle
// Default: 0 (Button A)
// Range: 0-2 (A, B, C)
#define AUTOMATION_TOGGLE_BUTTON 0

// Temperature sensor calibration offset
// Add to measured temperature if sensor reads consistently high/low
// Example: -0.5 if sensor reads 0.5°C too high
#define TEMP_CALIBRATION_OFFSET 0.0


// ============================================
// CLOUD SETTINGS
// ============================================

// Initial automation state on startup
// true: Automation enabled at startup
// false: Automation disabled at startup (manual mode)
#define AUTO_CONTROL_DEFAULT true

// Debug level for IoT Cloud
// 0: Errors only
// 1: Errors + Warnings
// 2: Errors + Warnings + Info (default)
// 3: Errors + Warnings + Info + Debug
#define DEBUG_LEVEL 2


// ============================================
// ADVANCED SETTINGS
// ============================================

// Enable serial debugging
#define ENABLE_SERIAL_DEBUG true

// Serial baud rate
#define SERIAL_BAUD_RATE 9600

// Button debounce delay (milliseconds)
#define BUTTON_DEBOUNCE_MS 50

// Number of temperature readings to average
// Higher = smoother but slower response
// Range: 1-10
#define TEMP_AVERAGING_SAMPLES 1


// ============================================
// GOOGLE HOME / IFTTT SETTINGS
// ============================================

// These are informational - actual control is via IoT Cloud + IFTTT

// Smart plug device name in Google Home
#define SMART_PLUG_NAME "Heater"

// IFTTT webhook event names (if using webhooks instead of cloud integration)
#define IFTTT_EVENT_HEATER_ON "arduino_heater_on"
#define IFTTT_EVENT_HEATER_OFF "arduino_heater_off"


// ============================================
// FEATURE FLAGS
// ============================================

// Enable/disable specific features

// Allow manual heater control when automation is disabled
#define ENABLE_MANUAL_CONTROL true

// Allow button to toggle automation
#define ENABLE_BUTTON_TOGGLE true

// Display temperature in Fahrenheit (in addition to Celsius)
#define ENABLE_FAHRENHEIT false


// ============================================
// TEMPERATURE CONVERSION
// ============================================

// Convert Celsius to Fahrenheit
inline float celsiusToFahrenheit(float celsius) {
  return (celsius * 9.0 / 5.0) + 32.0;
}

// Convert Fahrenheit to Celsius
inline float fahrenheitToCelsius(float fahrenheit) {
  return (fahrenheit - 32.0) * 5.0 / 9.0;
}

#endif // CONFIG_H
