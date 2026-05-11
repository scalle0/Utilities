#include <WiFi.h>
#include <WebServer.h>

const char* AP_SSID = "ESP32-Hotspot";

const IPAddress AP_IP(192, 168, 4, 1);
const IPAddress AP_GATEWAY(192, 168, 4, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);

WebServer server(80);

static String formatUptime(unsigned long ms) {
  unsigned long s = ms / 1000;
  unsigned long h = s / 3600;
  unsigned long m = (s % 3600) / 60;
  unsigned long sec = s % 60;
  char buf[16];
  snprintf(buf, sizeof(buf), "%luh %02lum %02lus", h, m, sec);
  return String(buf);
}

static void handleRoot() {
  String html = F(
    "<!doctype html><html><head>"
    "<meta charset=\"utf-8\">"
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
    "<meta http-equiv=\"refresh\" content=\"5\">"
    "<title>ESP32 Hotspot</title>"
    "<style>"
    "body{font-family:system-ui,sans-serif;margin:2em;color:#222}"
    "h1{margin-bottom:0}"
    "table{border-collapse:collapse;margin-top:1em}"
    "th,td{padding:.4em .8em;border-bottom:1px solid #ddd;text-align:left}"
    "th{background:#f4f4f4}"
    "</style></head><body>"
    "<h1>ESP32 Hotspot</h1>"
    "<p>You are connected to the ESP32 access point.</p>"
    "<table>"
    "<tr><th>SSID</th><td>");
  html += AP_SSID;
  html += F("</td></tr><tr><th>AP IP</th><td>");
  html += WiFi.softAPIP().toString();
  html += F("</td></tr><tr><th>Connected clients</th><td>");
  html += String(WiFi.softAPgetStationNum());
  html += F("</td></tr><tr><th>Uptime</th><td>");
  html += formatUptime(millis());
  html += F("</td></tr></table>"
    "<p style=\"margin-top:2em;color:#888;font-size:.9em\">"
    "Auto-refresh every 5s &middot; <a href=\"/status\">/status</a> for JSON"
    "</p></body></html>");
  server.send(200, "text/html", html);
}

static void handleStatus() {
  String json = "{";
  json += "\"ssid\":\"";    json += AP_SSID;                          json += "\",";
  json += "\"ip\":\"";      json += WiFi.softAPIP().toString();        json += "\",";
  json += "\"clients\":";   json += String(WiFi.softAPgetStationNum()); json += ",";
  json += "\"uptime_ms\":"; json += String(millis());
  json += "}";
  server.send(200, "application/json", json);
}

static void handleNotFound() {
  server.send(404, "text/plain", "Not found");
}

void setup() {
  Serial.begin(115200);
  delay(100);

  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);
  WiFi.softAP(AP_SSID);

  server.on("/", handleRoot);
  server.on("/status", handleStatus);
  server.onNotFound(handleNotFound);
  server.begin();

  Serial.println();
  Serial.println("AP started");
  Serial.print("SSID: "); Serial.println(AP_SSID);
  Serial.print("IP:   "); Serial.println(WiFi.softAPIP());
}

void loop() {
  server.handleClient();
}
