// ESP32 WiFi awareness demo: open AP + captive portal + educational landing page.
// Now with a persistent visitor counter and RGB LED feedback for live demos.
//
// Hardware: Arduino Nano ESP32 (ESP32-S3 with onboard RGB LED).
// Page lives on LittleFS — upload data/ separately. See README.md.

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <LittleFS.h>
#include <Preferences.h>

const char* AP_SSID = "ScAIdev";

const IPAddress AP_IP(192, 168, 4, 1);
const IPAddress AP_GATEWAY(192, 168, 4, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);

const byte DNS_PORT = 53;

// LED durations.
const unsigned long GREEN_FLASH_MS = 1500;
const unsigned long RED_BLINK_PERIOD_MS = 2000;

WebServer   server(80);
DNSServer   dnsServer;
Preferences prefs;

uint32_t      totalVisitors      = 0;
unsigned long greenFlashUntilMs  = 0;

// RGB LED on the Nano ESP32 is wired active-LOW.
static void rgb(bool r, bool g, bool b) {
  digitalWrite(LED_RED,   r ? LOW : HIGH);
  digitalWrite(LED_GREEN, g ? LOW : HIGH);
  digitalWrite(LED_BLUE,  b ? LOW : HIGH);
}

static void onWiFiEvent(WiFiEvent_t event) {
  if (event == ARDUINO_EVENT_WIFI_AP_STACONNECTED) {
    totalVisitors++;
    prefs.putUInt("visitors", totalVisitors);
    greenFlashUntilMs = millis() + GREEN_FLASH_MS;
    Serial.print("New client. Total visitors: ");
    Serial.println(totalVisitors);
  }
}

static void streamFromFs(const char* path, const char* contentType) {
  File f = LittleFS.open(path, "r");
  if (!f) {
    server.send(500, "text/plain",
                "File missing from LittleFS. Upload the data/ folder.");
    return;
  }
  server.streamFile(f, contentType);
  f.close();
}

static void handleRoot()   { streamFromFs("/index.html",  "text/html"); }
static void handleGotcha() { streamFromFs("/gotcha.html", "text/html"); }

static void handleStatus() {
  String json = "{";
  json += "\"ssid\":\"";          json += AP_SSID;                            json += "\",";
  json += "\"ip\":\"";            json += WiFi.softAPIP().toString();          json += "\",";
  json += "\"clients\":";         json += String(WiFi.softAPgetStationNum());  json += ",";
  json += "\"total_visitors\":";  json += String(totalVisitors);               json += ",";
  json += "\"uptime_ms\":";       json += String(millis());
  json += "}";
  server.send(200, "application/json", json);
}

static void handleCaptive() {
  server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString() + "/", true);
  server.send(302, "text/plain", "");
}

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) {
    delay(10);
  }

  pinMode(LED_RED,   OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE,  OUTPUT);
  rgb(false, false, false);

  if (!LittleFS.begin(false)) {
    Serial.println("LittleFS mount failed. Did you upload the data/ folder?");
  }

  prefs.begin("scaidev", false);
  totalVisitors = prefs.getUInt("visitors", 0);
  Serial.print("Loaded visitor count: ");
  Serial.println(totalVisitors);

  WiFi.onEvent(onWiFiEvent);
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);
  WiFi.softAP(AP_SSID);

  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(DNS_PORT, "*", AP_IP);

  server.on("/generate_204",              handleCaptive);  // Android
  server.on("/gen_204",                   handleCaptive);  // Android (older)
  server.on("/hotspot-detect.html",       handleCaptive);  // iOS / macOS
  server.on("/library/test/success.html", handleCaptive);  // iOS
  server.on("/connecttest.txt",           handleCaptive);  // Windows 10+
  server.on("/ncsi.txt",                  handleCaptive);  // Windows
  server.on("/redirect",                  handleCaptive);  // Windows
  server.on("/",                          handleRoot);
  server.on("/gotcha",                    handleGotcha);
  server.on("/status",                    handleStatus);
  // Static assets used by the landing page.
  server.serveStatic("/audio/", LittleFS, "/audio/");
  server.serveStatic("/fonts/", LittleFS, "/fonts/");
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

  if (millis() < greenFlashUntilMs) {
    rgb(false, true, false);
  } else {
    bool on = (millis() % RED_BLINK_PERIOD_MS) < 80;
    rgb(on, false, false);
  }
}
