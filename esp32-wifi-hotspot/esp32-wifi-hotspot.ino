// ESP32 WiFi awareness demo: open AP + captive portal + educational landing page.
// The page itself lives on the ESP32's LittleFS partition as /index.html.
// Upload it once with the arduino-littlefs-upload plugin (Arduino IDE 2.x) or
// PlatformIO's "Upload Filesystem Image" target. Edit data/index.html freely
// without recompiling C++.

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <LittleFS.h>

const char* AP_SSID = "ScAIdev";

const IPAddress AP_IP(192, 168, 4, 1);
const IPAddress AP_GATEWAY(192, 168, 4, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);

const byte DNS_PORT = 53;

WebServer  server(80);
DNSServer  dnsServer;

static void handleRoot() {
  File f = LittleFS.open("/index.html", "r");
  if (!f) {
    server.send(500, "text/plain",
                "index.html missing from LittleFS. Upload the data/ folder.");
    return;
  }
  server.streamFile(f, "text/html");
  f.close();
}

static void handleStatus() {
  String json = "{";
  json += "\"ssid\":\"";    json += AP_SSID;                            json += "\",";
  json += "\"ip\":\"";      json += WiFi.softAPIP().toString();          json += "\",";
  json += "\"clients\":";   json += String(WiFi.softAPgetStationNum());  json += ",";
  json += "\"uptime_ms\":"; json += String(millis());
  json += "}";
  server.send(200, "application/json", json);
}

// Catch-all: redirect everything to the landing page. This is what makes
// phones/laptops pop the captive-portal sheet automatically.
static void handleCaptive() {
  server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString() + "/", true);
  server.send(302, "text/plain", "");
}

void setup() {
  Serial.begin(115200);
  // Arduino Nano ESP32 uses native USB CDC: wait briefly for the host to
  // enumerate so the boot log isn't lost on first Serial Monitor open.
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) {
    delay(10);
  }

  if (!LittleFS.begin(false)) {
    Serial.println("LittleFS mount failed. Did you upload the data/ folder?");
  }

  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);
  WiFi.softAP(AP_SSID);

  // DNS hijack: answer every lookup with our own IP so any URL the OS
  // probes (or the user types) lands on us.
  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(DNS_PORT, "*", AP_IP);

  // OS-specific captive-portal probe URLs. Returning a redirect on these
  // tells Android/iOS/Windows "you're behind a portal" and they auto-open it.
  server.on("/generate_204",              handleCaptive);  // Android
  server.on("/gen_204",                   handleCaptive);  // Android (older)
  server.on("/hotspot-detect.html",       handleCaptive);  // iOS / macOS
  server.on("/library/test/success.html", handleCaptive);  // iOS
  server.on("/connecttest.txt",           handleCaptive);  // Windows 10+
  server.on("/ncsi.txt",                  handleCaptive);  // Windows
  server.on("/redirect",                  handleCaptive);  // Windows
  server.on("/",                          handleRoot);
  server.on("/status",                    handleStatus);
  server.onNotFound(handleCaptive);
  server.begin();

  Serial.println();
  Serial.println("Captive demo AP started");
  Serial.print("SSID: "); Serial.println(AP_SSID);
  Serial.print("IP:   "); Serial.println(WiFi.softAPIP());
}

void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
}
