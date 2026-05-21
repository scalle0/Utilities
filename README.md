# Utilities — Uno Q local LLM chatbot

A small local-LLM chatbot that runs on an Arduino Uno Q, with an optional
RPC bridge to the on-board STM32 microcontroller so the model can drive
GPIO. Browser UI, no cloud.

```
[ Phone / laptop on same WiFi ]
            │  HTTP / WebSocket
            ▼
[ Uno Q — Linux side ]
   ├─ FastAPI + static chat UI       (server/)
   ├─ Ollama runtime (qwen2.5:1.5b)
   └─ Bridge to STM32 MCU            (server/bridge.py + firmware/)
            │  MessagePack-RPC over /var/run/arduino-router.sock
            ▼
[ STM32U585 MCU running Arduino_RouterBridge ]
```

## Status

End-to-end working: chat in the browser drives Ollama, Ollama tool-calls
land on the MCU via the Arduino router, and results stream back into the
conversation. Verified with `qwen2.5:1.5b` on the 1.7 GiB Uno Q.

## Layout

| Path | Role |
|---|---|
| `server/app.py` | FastAPI app — chat endpoint, bridge endpoints, static UI mount |
| `server/bridge.py` | Async MessagePack-RPC client speaking to `arduino-router.sock` |
| `server/tools.py` | Ollama tool schemas + dispatcher to the bridge |
| `server/static/` | Browser chat UI |
| `firmware/uno_q_bridge/uno_q_bridge.ino` | MCU sketch — registers RPC handlers via `Arduino_RouterBridge` |
| `setup.sh` | Installs Ollama, pulls the model, creates the Python venv |
| `run.sh` | Boots Ollama (if needed) and uvicorn |
| `install-service.sh` | Installs the `uno-chat.service` systemd unit |

## First-time setup (Linux side)

```bash
git clone https://github.com/scalle0/Utilities.git
cd Utilities
./setup.sh                # installs Ollama, pulls the model, creates venv
./install-service.sh      # registers and starts uno-chat.service
```

The chatbot is then on `http://<uno-q-ip>:8080` from any device on the
same WiFi.

## Flashing the MCU bridge firmware

1. Open `firmware/uno_q_bridge/uno_q_bridge.ino` in the Arduino IDE.
2. Install the **Arduino_RouterBridge** library via Library Manager.
3. Select the Uno Q MCU (STM32U585) board target.
4. Upload.

After upload the Linux side should report the bridge as connected:

```bash
curl localhost:8080/api/bridge/health
# {"connected":true,"port":"/var/run/arduino-router.sock"}
```

## Tools exposed to the LLM

The model is given four tools when the bridge is connected:

| Tool | Args | Returns |
|---|---|---|
| `ping` | — | `"pong"` |
| `gpio_mode` | `pin: int`, `mode: "input" \| "input_pullup" \| "output"` | `bool` |
| `gpio_write` | `pin: int`, `value: bool` | `bool` |
| `gpio_read` | `pin: int` | `0` or `1` |

Each invocation surfaces in the UI as a `→ tool_name({args}) = result`
line and in the journal as `[tool]` lines.

## Direct bridge calls (without the LLM)

Useful for testing firmware and bridge plumbing without going through
the model:

```bash
curl -X POST localhost:8080/api/bridge/call \
  -H 'content-type: application/json' \
  -d '{"method":"ping"}'

curl -X POST localhost:8080/api/bridge/call \
  -H 'content-type: application/json' \
  -d '{"method":"gpio_mode","args":[13,"output"]}'

curl -X POST localhost:8080/api/bridge/call \
  -H 'content-type: application/json' \
  -d '{"method":"gpio_write","args":[13,true]}'
```

## Configuration (env vars)

| Variable | Default | Purpose |
|---|---|---|
| `UNO_CHAT_MODEL` | `qwen2.5:1.5b` | Ollama model tag |
| `UNO_CHAT_PORT` | `8080` | HTTP port |
| `UNO_CHAT_SYSTEM` | (built-in prompt) | System prompt prefix |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama endpoint |
| `BRIDGE_SOCK` | `/var/run/arduino-router.sock` | Router socket path |
| `BRIDGE_ENABLED` | `1` | Set to `0` to disable bridge integration |
| `BRIDGE_TIMEOUT` | `5.0` | Seconds to wait per RPC call |

Override per-run:
```bash
sudo systemctl set-environment UNO_CHAT_MODEL=llama3.2:1b
sudo systemctl restart uno-chat
```

## Tailing what's happening

```bash
# Full service log
sudo journalctl -fu uno-chat

# Just chat / tool events
sudo journalctl -fu uno-chat | grep -E '\[chat\]|\[tool\]|\[bridge\]'

# MCU-side serial (from the Arduino router)
arduino-app-cli monitor

# Raw Ollama log
tail -f /tmp/ollama.log
```

## Memory notes

The Uno Q has ~1.7 GiB RAM. Models that fit comfortably:

| Model | Size | Notes |
|---|---|---|
| `qwen2.5:1.5b` | ~1.0 GB | Default. Tool-calls reliably. |
| `llama3.2:1b` | ~1.3 GB | Meta-trained for tools at 1B. Alternative. |
| `granite3-moe:1b` | ~820 MB | IBM MoE, tool-capable. |

Models that **OOM-kill** the service:

| Model | Size |
|---|---|
| `qwen2.5:3b` | 1.9 GB |
| `mistral:7b` | ~4 GB |
| `ministral:3b` | ~2 GB |

## What's next

Open items, roughly ordered:

- **Physical verification of an LED.** Confirm that `gpio_write(13, true)` actually lights something. Pin 13 may not be wired on the Uno Q — add name-based pin support (`LED3_R`, `LED4_G`, etc.) on the MCU side, matching the `unoq-pin-toggle` convention.
- **`temp.read`.** Re-add an on-chip temperature read for the STM32U585 (the previous JSON-RPC sketch had a stub gated on `ATEMP`; on Zephyr/U585 the ADC channel needs to be wired explicitly).
- **Analog read tool** (`analog_read(pin)`). One extra MCU handler and one extra Ollama tool. Opens the door to an LDR or any analog sensor.
- **Better LED abstraction tool.** A high-level `set_led(name, on)` would let the model say "turn on the red LED" without needing pin/mode awareness.
- **Sensor stream / pub-sub.** Right now every RPC is request/response. For continuous readings (accelerometer, temp), use `Bridge.notify()` from the MCU and surface it as server-sent events to the UI.
- **Persist conversation history.** Currently lives only in the browser tab. A `/api/sessions` endpoint backed by SQLite would survive reloads.
- **Authentication.** Anyone on the WiFi can talk to the bot and toggle GPIO. Add a token check before exposing this outside a trusted network.
- **Static IP / mDNS** for the Uno Q so the chat URL doesn't change.

## License / origin

Original purpose was an energy management system (Growatt integration);
the chatbot is a parallel experiment on the same device.
