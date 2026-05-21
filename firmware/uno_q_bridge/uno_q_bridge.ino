// Uno Q MCU-side bridge firmware.
// Speaks newline-delimited JSON-RPC over Serial at 115200 to the Linux side
// (see server/bridge.py). One request per line, one response per line.
//
// Requires the "ArduinoJson" library (v7) installed via the Arduino IDE
// Library Manager.

#include <ArduinoJson.h>

static const uint32_t BAUD = 115200;
static const size_t MAX_LINE = 256;

static String line;

void sendDoc(JsonDocument& doc) {
  serializeJson(doc, Serial);
  Serial.print('\n');
}

void sendError(long id, const char* msg) {
  JsonDocument resp;
  resp["id"] = id;
  resp["error"] = msg;
  sendDoc(resp);
}

void handle(JsonDocument& req) {
  long id = req["id"] | -1;
  const char* method = req["method"] | "";
  JsonVariantConst params = req["params"];

  JsonDocument resp;
  resp["id"] = id;

  if (strcmp(method, "ping") == 0) {
    resp["result"] = "pong";

  } else if (strcmp(method, "temp.read") == 0) {
#ifdef ATEMP
    resp["result"]["raw"] = analogRead(ATEMP);
#else
    sendError(id, "temp.read not supported on this core");
    return;
#endif

  } else if (strcmp(method, "gpio.mode") == 0) {
    int pin = params["pin"] | -1;
    const char* mode = params["mode"] | "";
    if (pin < 0) { sendError(id, "pin required"); return; }
    if (strcmp(mode, "input") == 0)              pinMode(pin, INPUT);
    else if (strcmp(mode, "input_pullup") == 0)  pinMode(pin, INPUT_PULLUP);
    else if (strcmp(mode, "output") == 0)        pinMode(pin, OUTPUT);
    else { sendError(id, "mode must be input|input_pullup|output"); return; }
    resp["result"] = true;

  } else if (strcmp(method, "gpio.read") == 0) {
    int pin = params["pin"] | -1;
    if (pin < 0) { sendError(id, "pin required"); return; }
    resp["result"] = digitalRead(pin);

  } else if (strcmp(method, "gpio.write") == 0) {
    int pin = params["pin"] | -1;
    int value = params["value"] | -1;
    if (pin < 0 || value < 0) { sendError(id, "pin and value required"); return; }
    digitalWrite(pin, value ? HIGH : LOW);
    resp["result"] = true;

  } else {
    sendError(id, "unknown method");
    return;
  }

  sendDoc(resp);
}

void setup() {
  Serial.begin(BAUD);
  uint32_t start = millis();
  while (!Serial && millis() - start < 3000) {}
  line.reserve(MAX_LINE);
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      if (line.length()) {
        JsonDocument req;
        DeserializationError err = deserializeJson(req, line);
        if (err) sendError(-1, "bad json");
        else     handle(req);
        line = "";
      }
    } else if (c != '\r') {
      if (line.length() >= MAX_LINE) line = "";
      line += c;
    }
  }
}
