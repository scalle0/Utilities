#include <WiFi.h>

const char* AP_SSID = "ScAIdev";

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) {
    delay(10);
  }

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID);

  Serial.println();
  Serial.print("SSID: "); Serial.println(AP_SSID);
  Serial.print("IP:   "); Serial.println(WiFi.softAPIP());
}

void loop() {
}
