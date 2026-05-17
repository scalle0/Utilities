#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>

const char* AP_SSID = "ScAIdev";

const IPAddress AP_IP(192, 168, 4, 1);
const IPAddress AP_GATEWAY(192, 168, 4, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);

const byte DNS_PORT = 53;

WebServer server(80);
DNSServer dnsServer;

const char GOTCHA_HTML[] PROGMEM = R"HTML(
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>gotcha</title>
  <style>
    html, body {
      margin: 0; height: 100%;
      display: flex; align-items: center; justify-content: center;
      background: #000; color: #fff;
      font-family: -apple-system, system-ui, sans-serif;
    }
    h1 { font-size: 20vw; margin: 0; letter-spacing: -0.05em; }
  </style>
</head>
<body><h1>gotcha</h1></body>
</html>
)HTML";

static void handleRoot() {
  server.send_P(200, "text/html", GOTCHA_HTML);
}

static void handleCaptive() {
  server.sendHeader("Location",
                    String("http://") + WiFi.softAPIP().toString() + "/",
                    true);
  server.send(302, "text/plain", "");
}

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) {
    delay(10);
  }

  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);
  WiFi.softAP(AP_SSID);

  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(DNS_PORT, "*", AP_IP);

  server.on("/generate_204",              handleCaptive);
  server.on("/gen_204",                   handleCaptive);
  server.on("/hotspot-detect.html",       handleCaptive);
  server.on("/library/test/success.html", handleCaptive);
  server.on("/connecttest.txt",           handleCaptive);
  server.on("/ncsi.txt",                  handleCaptive);
  server.on("/redirect",                  handleCaptive);
  server.on("/",                          handleRoot);
  server.onNotFound(handleCaptive);
  server.begin();

  Serial.println();
  Serial.print("SSID: "); Serial.println(AP_SSID);
  Serial.print("IP:   "); Serial.println(WiFi.softAPIP());
}

void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
}
