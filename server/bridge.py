import asyncio
import json
import os
from typing import Any

import serial
import serial.tools.list_ports

PORT = os.environ.get("BRIDGE_PORT", "")
BAUD = int(os.environ.get("BRIDGE_BAUD", "115200"))
TIMEOUT = float(os.environ.get("BRIDGE_TIMEOUT", "2.0"))
ENABLED = os.environ.get("BRIDGE_ENABLED", "1") not in ("0", "false", "False", "")

ALLOWED_METHODS = {
    "ping",
    "temp.read",
    "gpio.read",
    "gpio.write",
    "gpio.mode",
}


def _autodetect_port() -> str:
    for p in serial.tools.list_ports.comports():
        name = (p.device or "").lower()
        if "ttymcu" in name or "ttyacm" in name or "ttyusb" in name:
            return p.device
    return ""


class BridgeError(RuntimeError):
    pass


class SerialBridge:
    def __init__(self) -> None:
        self._ser: serial.Serial | None = None
        self._lock = asyncio.Lock()
        self._next_id = 1
        self._port = ""

    @property
    def connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    @property
    def port(self) -> str:
        return self._port

    async def open(self) -> None:
        if not ENABLED:
            return
        port = PORT or _autodetect_port()
        if not port:
            return
        self._ser = await asyncio.to_thread(
            serial.Serial, port, BAUD, timeout=TIMEOUT
        )
        self._port = port
        await asyncio.to_thread(self._ser.reset_input_buffer)

    async def close(self) -> None:
        if self._ser is not None:
            await asyncio.to_thread(self._ser.close)
            self._ser = None

    async def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        if method not in ALLOWED_METHODS:
            raise BridgeError(f"unknown method: {method}")
        if not self.connected:
            raise BridgeError("bridge not connected")

        req_id = self._next_id
        self._next_id += 1
        payload = json.dumps(
            {"id": req_id, "method": method, "params": params or {}}
        ).encode() + b"\n"

        async with self._lock:
            await asyncio.to_thread(self._ser.write, payload)
            line = await asyncio.to_thread(self._ser.readline)

        if not line:
            raise BridgeError("timeout waiting for STM32 response")
        try:
            obj = json.loads(line.decode().strip())
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BridgeError(f"bad response: {line!r}") from exc

        if obj.get("id") != req_id:
            raise BridgeError(f"id mismatch: sent {req_id}, got {obj.get('id')}")
        if "error" in obj:
            raise BridgeError(str(obj["error"]))
        return obj.get("result")


bridge = SerialBridge()
