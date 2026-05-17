// Arduino UNO R4 WiFi port of the ScAIdev public-WiFi awareness demo.
//
// Same lesson as the ESP32 version, but the R4's onboard 12x8 LED matrix
// scrolls "GOTCHA" on each new visit and shows the running count in idle.
//
// The R4's WiFi co-processor (ESP32-S3-MINI) is driven via WiFiS3, which
// doesn't ship with a WebServer or DNSServer the way the ESP32 core does
// for the Nano ESP32. So we hand-roll:
//   - a tiny HTTP server on WiFiServer (parse request line, respond)
//   - a minimal DNS responder on WiFiUDP that answers every query with our IP
//
// HTML page lives as a PROGMEM string at the bottom of this file.

#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <EEPROM.h>
#include "Arduino_LED_Matrix.h"

const char* AP_SSID = "ScAIdev";

WiFiServer    httpServer(80);
WiFiUDP       dnsUdp;
ArduinoLEDMatrix matrix;

const uint16_t EEPROM_COUNT_ADDR = 0;
uint32_t        totalVisitors    = 0;
unsigned long   nextMatrixUpdate = 0;
bool            scrollingGotcha  = false;
unsigned long   scrollUntilMs    = 0;

extern const char LANDING_PAGE[] PROGMEM;
extern const size_t LANDING_PAGE_LEN;

// ---------- LED matrix ----------------------------------------------------

static void matrixShowCount() {
  matrix.beginDraw();
  matrix.stroke(0xFFFFFFFF);
  matrix.textFont(Font_4x6);
  matrix.beginText(0, 1, 0xFFFFFF);
  matrix.print(totalVisitors);
  matrix.endText();
  matrix.endDraw();
}

static void matrixScrollGotcha() {
  matrix.beginDraw();
  matrix.stroke(0xFFFFFFFF);
  matrix.textScrollSpeed(70);
  matrix.textFont(Font_5x7);
  matrix.beginText(0, 1, 0xFFFFFF);
  matrix.print(" GOTCHA ");
  matrix.endTextAnimation(SCROLL_LEFT);
  matrix.endDraw();
}

// ---------- Visitor counter ----------------------------------------------

static void persistCount() {
  EEPROM.put(EEPROM_COUNT_ADDR, totalVisitors);
}

static void registerVisit() {
  totalVisitors++;
  persistCount();
  scrollingGotcha = true;
  scrollUntilMs   = millis() + 2500;
  matrixScrollGotcha();
  Serial.print("New visit. Total: ");
  Serial.println(totalVisitors);
}

// ---------- DNS hijack (catch-all responder) -----------------------------

// Parse a DNS query packet and build a response pointing at our IP.
// Returns response length, or 0 on parse failure.
static int buildDnsResponse(const uint8_t* q, int qlen, uint8_t* out, IPAddress ip) {
  if (qlen < 12) return 0;

  // Copy the question (header + question section) verbatim, then tack on
  // an answer record. Find end of QNAME (labels terminated by 0x00).
  int p = 12;
  while (p < qlen && q[p] != 0) {
    int labelLen = q[p];
    if (labelLen & 0xC0) return 0;   // pointer in question is unusual; bail
    p += labelLen + 1;
    if (p >= qlen) return 0;
  }
  if (p + 5 > qlen) return 0;
  int questionEnd = p + 5;            // null byte + QTYPE(2) + QCLASS(2)

  memcpy(out, q, questionEnd);

  // Set flags: standard response, recursion available, no error.
  out[2] = 0x81;
  out[3] = 0x80;
  // ANCOUNT = 1
  out[6] = 0x00; out[7] = 0x01;

  int o = questionEnd;
  // Name: pointer back to question name at offset 12.
  out[o++] = 0xC0; out[o++] = 0x0C;
  // TYPE A
  out[o++] = 0x00; out[o++] = 0x01;
  // CLASS IN
  out[o++] = 0x00; out[o++] = 0x01;
  // TTL = 60
  out[o++] = 0x00; out[o++] = 0x00; out[o++] = 0x00; out[o++] = 0x3C;
  // RDLENGTH = 4
  out[o++] = 0x00; out[o++] = 0x04;
  // RDATA = our IP
  out[o++] = ip[0]; out[o++] = ip[1]; out[o++] = ip[2]; out[o++] = ip[3];
  return o;
}

static void serviceDns() {
  int sz = dnsUdp.parsePacket();
  if (sz <= 0) return;

  uint8_t inBuf[512];
  uint8_t outBuf[512];
  int n = dnsUdp.read(inBuf, sizeof(inBuf));
  if (n <= 0) return;

  IPAddress ourIp = WiFi.localIP();
  int outLen = buildDnsResponse(inBuf, n, outBuf, ourIp);
  if (outLen <= 0) return;

  dnsUdp.beginPacket(dnsUdp.remoteIP(), dnsUdp.remotePort());
  dnsUdp.write(outBuf, outLen);
  dnsUdp.endPacket();
}

// ---------- HTTP server --------------------------------------------------

static void sendRedirectToRoot(WiFiClient& c, IPAddress ip) {
  String loc = String("http://") + ip.toString() + "/";
  c.println("HTTP/1.1 302 Found");
  c.print  ("Location: "); c.println(loc);
  c.println("Content-Length: 0");
  c.println("Connection: close");
  c.println();
}

static void sendStatus(WiFiClient& c) {
  IPAddress ip = WiFi.localIP();
  String body = "{";
  body += "\"ssid\":\"";          body += AP_SSID;            body += "\",";
  body += "\"ip\":\"";            body += ip.toString();       body += "\",";
  body += "\"total_visitors\":";  body += String(totalVisitors); body += ",";
  body += "\"uptime_ms\":";       body += String(millis());
  body += "}";
  c.println("HTTP/1.1 200 OK");
  c.println("Content-Type: application/json");
  c.print  ("Content-Length: "); c.println(body.length());
  c.println("Connection: close");
  c.println();
  c.print(body);
}

static void sendLanding(WiFiClient& c) {
  c.println("HTTP/1.1 200 OK");
  c.println("Content-Type: text/html; charset=utf-8");
  c.print  ("Content-Length: "); c.println(LANDING_PAGE_LEN);
  c.println("Connection: close");
  c.println();
  // Stream PROGMEM in chunks.
  const size_t CHUNK = 128;
  char buf[CHUNK + 1];
  for (size_t i = 0; i < LANDING_PAGE_LEN; i += CHUNK) {
    size_t n = min(CHUNK, LANDING_PAGE_LEN - i);
    memcpy_P(buf, LANDING_PAGE + i, n);
    c.write((uint8_t*)buf, n);
  }
}

static void serviceHttp() {
  WiFiClient client = httpServer.available();
  if (!client) return;

  // Read first line: "GET /path HTTP/1.1"
  String reqLine = client.readStringUntil('\n');
  // Drain remaining headers.
  while (client.connected() && client.available()) {
    String h = client.readStringUntil('\n');
    if (h.length() <= 1) break;
  }

  // Extract path.
  int sp1 = reqLine.indexOf(' ');
  int sp2 = reqLine.indexOf(' ', sp1 + 1);
  String path = (sp1 > 0 && sp2 > sp1) ? reqLine.substring(sp1 + 1, sp2) : String("/");

  IPAddress ip = WiFi.localIP();

  if (path == "/") {
    registerVisit();
    sendLanding(client);
  } else if (path == "/status") {
    sendStatus(client);
  } else {
    // Any other URL: 302 to landing. This is what makes phones pop the
    // captive-portal sheet automatically (Android /generate_204, iOS
    // /hotspot-detect.html, Windows /connecttest.txt, etc.).
    sendRedirectToRoot(client, ip);
  }

  client.flush();
  client.stop();
}

// ---------- Setup / loop -------------------------------------------------

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) {
    delay(10);
  }

  EEPROM.get(EEPROM_COUNT_ADDR, totalVisitors);
  if (totalVisitors == 0xFFFFFFFF) totalVisitors = 0;
  Serial.print("Loaded visitor count: "); Serial.println(totalVisitors);

  matrix.begin();
  matrixShowCount();

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi module not found.");
    while (true) { delay(1000); }
  }

  Serial.print("Starting AP: "); Serial.println(AP_SSID);
  int status = WiFi.beginAP(AP_SSID);
  if (status != WL_AP_LISTENING) {
    Serial.println("AP failed to start.");
    while (true) { delay(1000); }
  }

  httpServer.begin();
  dnsUdp.begin(53);

  Serial.print("AP IP: "); Serial.println(WiFi.localIP());
  Serial.println("Captive demo AP listening.");
}

void loop() {
  serviceDns();
  serviceHttp();

  if (scrollingGotcha && millis() > scrollUntilMs) {
    scrollingGotcha = false;
    matrixShowCount();
  }
  // Periodic refresh of idle matrix display so the count keeps showing.
  if (!scrollingGotcha && millis() > nextMatrixUpdate) {
    matrixShowCount();
    nextMatrixUpdate = millis() + 5000;
  }
}

// ---------- Landing page (PROGMEM) ---------------------------------------
// No LittleFS on the Renesas side, so the HTML lives in flash here. Keep
// it short — the R4 has 256 KB of flash but only ~32 KB of SRAM, and we
// stream this in chunks.

const char LANDING_PAGE[] PROGMEM =
  "<!doctype html><html><head>"
  "<meta charset=\"utf-8\">"
  "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
  "<title>Gotcha!</title>"
  "<style>"
  "body{font-family:system-ui,sans-serif;margin:0;"
  "background:linear-gradient(135deg,#1a1a2e,#16213e);color:#eee;"
  "min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5em}"
  ".card{max-width:560px;background:#0f3460;padding:2em;border-radius:12px;"
  "box-shadow:0 10px 40px rgba(0,0,0,.5)}"
  "h1{margin:0 0 .2em;font-size:2.2em;color:#e94560}"
  "h2{color:#f5b14f;margin-top:1.4em}"
  "ul{padding-left:1.2em;line-height:1.6}li{margin:.3em 0}"
  ".muted{color:#9aa;font-size:.85em;margin-top:2em}"
  "</style></head><body><div class=\"card\">"
  "<h1>Gotcha.</h1>"
  "<p>You just joined an open WiFi network called <strong>ScAIdev</strong> "
  "you've never seen before, and your phone happily opened this page. "
  "If I were not a friend, right now I could be:</p>"
  "<ul>"
  "<li>Watching every plain HTTP site you visit</li>"
  "<li>Serving you a fake login page for your bank, email, or socials</li>"
  "<li>Injecting ads or malware into pages you load</li>"
  "<li>Sniffing app traffic that isn't properly encrypted</li>"
  "</ul>"
  "<p>The setup? An Arduino the size of a credit card, about 200 lines "
  "of code, and a USB battery in someone's backpack.</p>"
  "<h2>How to stay safer on public WiFi</h2>"
  "<ul>"
  "<li>Don't auto-join networks named &ldquo;Free WiFi&rdquo; or &ldquo;Guest&rdquo;</li>"
  "<li>Turn off &ldquo;auto-connect to open networks&rdquo; on your phone</li>"
  "<li>Use a VPN on networks you don't trust</li>"
  "<li>Check the padlock in your browser &mdash; if it's missing, leave</li>"
  "<li>When in doubt, use your phone's mobile data instead</li>"
  "</ul>"
  "<p class=\"muted\">No data was collected. Stay curious, stay paranoid. &mdash; ScAIdev</p>"
  "</div></body></html>";

const size_t LANDING_PAGE_LEN = sizeof(LANDING_PAGE) - 1;
