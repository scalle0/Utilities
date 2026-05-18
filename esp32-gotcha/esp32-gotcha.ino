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

const char HTML_HEAD[] PROGMEM = R"HTML(<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>You just joined an open Wi-Fi network</title>
  <style>
    :root {
      --bg: #F4F1EA;
      --surface: #FFFFFF;
      --border: #E5E1D6;
      --ink: #1F2933;
      --muted: #5C6470;
      --green: #0F7A5A;
      --blue: #1A4D80;
      --amber: #B8741A;
    }
    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0;
      background: var(--bg); color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui,
                   Roboto, sans-serif;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }
    main {
      max-width: 680px;
      margin: 40px auto;
      padding: 0 16px;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 32px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    @media (min-width: 640px) {
      .card { padding: 48px; }
    }
    h1 {
      color: var(--green);
      font-size: 1.9rem;
      line-height: 1.2;
      margin: 0 0 12px;
      letter-spacing: -0.01em;
    }
    h2 {
      font-size: 1.05rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--green);
      margin: 32px 0 12px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--border);
    }
    p { margin: 0 0 14px; color: var(--ink); }
    p.lede { color: var(--muted); font-size: 1.05rem; }
    dl.readout {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      margin: 0;
    }
    @media (min-width: 520px) {
      dl.readout { grid-template-columns: 180px 1fr; gap: 10px 18px; }
    }
    dt {
      color: var(--blue);
      font-weight: 600;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      align-self: center;
    }
    dd {
      margin: 0;
      font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
      font-size: 0.9rem;
      color: var(--ink);
      word-break: break-word;
      background: #FAF8F2;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 10px;
    }
    ul.risks { padding-left: 20px; margin: 0; }
    ul.risks li {
      margin-bottom: 10px;
      color: var(--ink);
    }
    ul.risks li strong { color: var(--amber); }
    .reassure {
      background: #EEF6F2;
      border-left: 3px solid var(--green);
      padding: 16px 18px;
      border-radius: 6px;
      margin-top: 8px;
    }
    .reassure p:last-child { margin-bottom: 0; }
    footer {
      text-align: center;
      color: var(--muted);
      font-size: 0.85rem;
      margin-top: 28px;
    }
  </style>
</head>
<body>
<main>
<div class="card">
  <h1>You just joined an open Wi-Fi network.</h1>
  <p class="lede">
    Any device on this access point is visible to whoever operates it.
    Here's exactly what this network just read from your device.
  </p>

  <h2>What this access point sees about you right now</h2>
  <dl class="readout">
)HTML";

const char HTML_TAIL[] PROGMEM = R"HTML(
  </dl>

  <h2>What a malicious operator could do</h2>
  <ul class="risks">
    <li><strong>Hijack DNS.</strong> Every domain your device looks up passes
    through this access point. A hostile operator can redirect lookups to
    fake servers — including phony captive-portal login pages.</li>
    <li><strong>Strip and downgrade traffic.</strong> Anything you load over
    plain HTTP can be read or modified in flight. HTTPS prevents most of this,
    but mixed content and misconfigured apps still leak.</li>
    <li><strong>Phish credentials.</strong> A lookalike Wi-Fi login or app
    login page on this network can harvest usernames, passwords, or 2FA codes
    from anyone who types them in.</li>
  </ul>

  <h2>What this demo does with that data</h2>
  <div class="reassure">
    <p>
      Nothing is stored. The values above were read from your HTTP request,
      rendered once into this page, and discarded the moment the response
      finished sending.
    </p>
    <p>
      No logging to flash, no upload to any server, no analytics. The full
      sketch source is public, so you can verify that yourself.
    </p>
  </div>

  <footer>ScAIdev awareness demo</footer>
</div>
</main>
</body>
</html>
)HTML";

static String escapeHtml(const String& in) {
  String out;
  out.reserve(in.length() + 8);
  for (size_t i = 0; i < in.length(); i++) {
    char c = in[i];
    switch (c) {
      case '&':  out += "&amp;";  break;
      case '<':  out += "&lt;";   break;
      case '>':  out += "&gt;";   break;
      case '"':  out += "&quot;"; break;
      case '\'': out += "&#39;";  break;
      default:   out += c;        break;
    }
  }
  return out;
}

static String readout(const String& label, const String& value) {
  String safe = value;
  if (safe.length() == 0) safe = "(not provided)";
  if (safe.length() > 200) safe = safe.substring(0, 200) + "…";
  String row = "    <dt>";
  row += label;
  row += "</dt>\n    <dd>";
  row += escapeHtml(safe);
  row += "</dd>\n";
  return row;
}

static void handleRoot() {
  String clientIp = server.client().remoteIP().toString();
  String ua       = server.header("User-Agent");
  String lang     = server.header("Accept-Language");
  String host     = server.header("Host");
  String uri      = server.uri();
  String reached  = host.length() ? (host + uri) : uri;
  String clients  = String(WiFi.softAPgetStationNum());

  String dyn;
  dyn.reserve(1200);
  dyn += readout("Your IP here",     clientIp);
  dyn += readout("Your device",      ua);
  dyn += readout("Preferred langs",  lang);
  dyn += readout("URL intercepted",  reached);
  dyn += readout("Other clients",    clients);

  server.setContentLength(CONTENT_LENGTH_UNKNOWN);
  server.send(200, "text/html", "");
  server.sendContent_P(HTML_HEAD);
  server.sendContent(dyn);
  server.sendContent_P(HTML_TAIL);
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

  const char* hdrs[] = { "User-Agent", "Accept-Language", "Host" };
  server.collectHeaders(hdrs, sizeof(hdrs) / sizeof(hdrs[0]));

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
