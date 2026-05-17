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
      margin: 0; height: 100%; overflow: hidden;
      background: #000; color: #fff;
      font-family: -apple-system, system-ui, sans-serif;
    }
    canvas { position: fixed; inset: 0; width: 100%; height: 100%; }
    h1 {
      position: fixed; inset: 0;
      display: flex; align-items: center; justify-content: center;
      margin: 0; font-size: 20vw; letter-spacing: -0.05em;
      text-shadow: 0 0 24px rgba(255,255,255,0.6);
      pointer-events: none;
    }
  </style>
</head>
<body>
  <canvas id="fx"></canvas>
  <h1>gotcha</h1>
  <script>
    const c = document.getElementById('fx');
    const x = c.getContext('2d');
    let W, H;
    function resize() { W = c.width = innerWidth; H = c.height = innerHeight; }
    addEventListener('resize', resize); resize();

    const particles = [];
    const G = 0.05;

    function burst(px, py) {
      const hue = Math.floor(Math.random() * 360);
      const n = 60 + Math.floor(Math.random() * 40);
      for (let i = 0; i < n; i++) {
        const a = Math.random() * Math.PI * 2;
        const s = Math.random() * 4 + 1;
        particles.push({
          x: px, y: py,
          vx: Math.cos(a) * s, vy: Math.sin(a) * s,
          life: 1, hue: hue + Math.random() * 30 - 15
        });
      }
    }

    function tick() {
      x.fillStyle = 'rgba(0,0,0,0.18)';
      x.fillRect(0, 0, W, H);
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.vy += G;
        p.x += p.vx; p.y += p.vy;
        p.life -= 0.012;
        if (p.life <= 0) { particles.splice(i, 1); continue; }
        x.fillStyle = 'hsla(' + p.hue + ',100%,60%,' + p.life + ')';
        x.fillRect(p.x, p.y, 2, 2);
      }
      if (Math.random() < 0.04) {
        burst(Math.random() * W, Math.random() * H * 0.6);
      }
      requestAnimationFrame(tick);
    }
    tick();
    addEventListener('click', e => burst(e.clientX, e.clientY));
    addEventListener('touchstart', e => {
      for (const t of e.touches) burst(t.clientX, t.clientY);
    });
  </script>
</body>
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
