import asyncio
import os

import msgpack

SOCK_PATH = os.environ.get("BRIDGE_SOCK", "/var/run/arduino-router.sock")
ENABLED = os.environ.get("BRIDGE_ENABLED", "1") not in ("0", "false", "False", "")
CALL_TIMEOUT = float(os.environ.get("BRIDGE_TIMEOUT", "5.0"))

TYPE_REQUEST = 0
TYPE_RESPONSE = 1
TYPE_NOTIFY = 2

ALLOWED_METHODS = {"ping", "gpio_mode", "gpio_read", "gpio_write"}


class BridgeError(RuntimeError):
    pass


class RouterBridge:
    def __init__(self) -> None:
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._reader_task: asyncio.Task | None = None
        self._pending: dict[int, asyncio.Future] = {}
        self._next_id = 1
        self._sock_path = ""
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def port(self) -> str:
        return self._sock_path

    async def open(self) -> None:
        if not ENABLED or not os.path.exists(SOCK_PATH):
            return
        self._reader, self._writer = await asyncio.open_unix_connection(SOCK_PATH)
        self._sock_path = SOCK_PATH
        self._connected = True
        self._reader_task = asyncio.create_task(self._read_loop())

    async def close(self) -> None:
        self._connected = False
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except (asyncio.CancelledError, Exception):
                pass
            self._reader_task = None
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = self._writer = None

    async def _read_loop(self) -> None:
        unpacker = msgpack.Unpacker(raw=False, use_list=True)
        try:
            while True:
                chunk = await self._reader.read(4096)
                if not chunk:
                    break
                unpacker.feed(chunk)
                for msg in unpacker:
                    self._dispatch(msg)
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        finally:
            self._connected = False
            for fut in self._pending.values():
                if not fut.done():
                    fut.set_exception(BridgeError("router connection lost"))
            self._pending.clear()

    def _dispatch(self, msg) -> None:
        if not isinstance(msg, list) or not msg:
            return
        if msg[0] == TYPE_RESPONSE and len(msg) == 4:
            _, msg_id, error, result = msg
            fut = self._pending.pop(msg_id, None)
            if fut is None or fut.done():
                return
            if error is not None:
                fut.set_exception(BridgeError(_format_error(error)))
            else:
                fut.set_result(result)

    async def call(self, method: str, args: list | None = None) -> object:
        if method not in ALLOWED_METHODS:
            raise BridgeError(f"unknown method: {method}")
        if not self._connected or self._writer is None:
            raise BridgeError("bridge not connected")

        msg_id = self._next_id & 0xFFFFFFFF
        self._next_id += 1
        frame = msgpack.packb(
            [TYPE_REQUEST, msg_id, method, list(args or [])], use_bin_type=True
        )

        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[msg_id] = fut

        self._writer.write(frame)
        try:
            await self._writer.drain()
            return await asyncio.wait_for(fut, timeout=CALL_TIMEOUT)
        except asyncio.TimeoutError:
            self._pending.pop(msg_id, None)
            raise BridgeError(f"timeout calling {method}")


def _format_error(err) -> str:
    if isinstance(err, list) and len(err) >= 2:
        return f"rpc error {err[0]}: {err[1]}"
    return str(err)


bridge = RouterBridge()
