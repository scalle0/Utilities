// ESP32 WiFi awareness demo: open AP + captive portal + educational landing page.
// Intended for classrooms, meetups, and your own venues. Do not impersonate real
// networks (e.g. "Starbucks WiFi") or collect credentials.

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>

const char* AP_SSID    = "ScAIdev";
const char* DEMO_OWNER = "Your friendly neighborhood demo";

const IPAddress AP_IP(192, 168, 4, 1);
const IPAddress AP_GATEWAY(192, 168, 4, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);

const byte DNS_PORT = 53;

WebServer  server(80);
DNSServer  dnsServer;

static void handleRoot() {
  String html = F(
    "<!doctype html><html><head>"
    "<meta charset=\"utf-8\">"
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
    "<title>Gotcha!</title>"
    "<style>"
    "body{font-family:system-ui,-apple-system,sans-serif;margin:0;"
    "background:linear-gradient(135deg,#1a1a2e,#16213e);color:#eee;"
    "min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5em}"
    ".card{max-width:560px;background:#0f3460;padding:2em;border-radius:12px;"
    "box-shadow:0 10px 40px rgba(0,0,0,.5)}"
    "h1{margin:0 0 .2em;font-size:2.2em;color:#e94560}"
    "h2{color:#f5b14f;margin-top:1.4em}"
    "ul{padding-left:1.2em;line-height:1.6}"
    "li{margin:.3em 0}"
    "code{background:#1a1a2e;padding:.1em .4em;border-radius:4px;font-size:.95em}"
    ".muted{color:#9aa;font-size:.85em;margin-top:2em}"
    "</style></head><body><div class=\"card\">"
    "<h1>Gotcha.</h1>"
    "<p>You just joined an open WiFi network you've never seen before "
    "and your phone happily opened this page. If I were not a friend, "
    "right now I could be:</p>"
    "<ul>"
    "<li>Watching every plain HTTP site you visit</li>"
    "<li>Serving you a fake login page for your bank, email, or socials</li>"
    "<li>Injecting ads or malware into pages you load</li>"
    "<li>Sniffing app traffic that isn't properly encrypted</li>"
    "</ul>"
    "<p>The setup? An <code>ESP32</code> the size of a stick of gum, about "
    "100 lines of code, and a USB battery in someone's backpack.</p>"
    "<h2>How to stay safer on public WiFi</h2>"
    "<ul>"
    "<li>Don't auto-join networks named &ldquo;Free WiFi,&rdquo; &ldquo;Airport,&rdquo; &ldquo;Guest&rdquo;</li>"
    "<li>Turn off &ldquo;auto-connect to open networks&rdquo; in your phone settings</li>"
    "<li>Use a VPN when you're not on a network you trust</li>"
    "<li>Check the <strong>padlock</strong> in your browser — if it's missing, leave</li>"
    "<li>When in doubt, tether off your phone's mobile data instead</li>"
    "</ul>"
    "<p class=\"muted\">No data was collected. This page is harmless. "
    "Stay curious, stay paranoid. — ");
  html += DEMO_OWNER;
  html += F("</p></div></body></html>");
  server.send(200, "text/html", html);
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
  delay(100);

  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);
  WiFi.softAP(AP_SSID);

  // DNS hijack: answer every lookup with our own IP so any URL the OS
  // probes (or the user types) lands on us.
  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(DNS_PORT, "*", AP_IP);

  // OS-specific captive-portal probe URLs. Returning a redirect on these
  // tells Android/iOS/Windows "you're behind a portal" and they auto-open it.
  server.on("/generate_204",          handleCaptive);   // Android
  server.on("/gen_204",                handleCaptive);   // Android (older)
  server.on("/hotspot-detect.html",    handleCaptive);   // iOS / macOS
  server.on("/library/test/success.html", handleCaptive); // iOS
  server.on("/connecttest.txt",        handleCaptive);   // Windows 10+
  server.on("/ncsi.txt",               handleCaptive);   // Windows
  server.on("/redirect",               handleCaptive);   // Windows
  server.on("/",                       handleRoot);
  server.on("/status",                 handleStatus);
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
