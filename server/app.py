import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from bridge import BridgeError, bridge
from tools import TOOLS, dispatch as dispatch_tool

MAX_TOOL_ROUNDS = 5

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("UNO_CHAT_MODEL", "qwen2.5:1.5b")
SYSTEM_PROMPT = os.environ.get(
    "UNO_CHAT_SYSTEM",
    "You are a small assistant running locally on an Arduino Uno Q. "
    "Be concise. If you don't know, say so.",
)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await bridge.open()
    except Exception as exc:
        print(f"[bridge] open failed: {exc!r}", flush=True)
    try:
        yield
    finally:
        await bridge.close()


app = FastAPI(title="Uno Q Chat", lifespan=lifespan)


@app.get("/health")
async def health():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            tags = [m["name"] for m in r.json().get("models", [])]
            return {"ok": True, "model": DEFAULT_MODEL, "available": tags}
        except Exception as exc:
            return {"ok": False, "model": DEFAULT_MODEL, "error": str(exc)}


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = list(body.get("messages", []))
    model = body.get("model", DEFAULT_MODEL)

    use_tools = bridge.connected
    if SYSTEM_PROMPT and not (messages and messages[0].get("role") == "system"):
        system = SYSTEM_PROMPT
        if use_tools:
            system += (
                " You can control hardware on the STM32 microcontroller via the "
                "provided tools (ping, gpio_mode, gpio_write, gpio_read). Use them "
                "when the user asks to turn things on/off, blink a light, or read "
                "an input. Configure pin mode before reading or writing."
            )
        messages = [{"role": "system", "content": system}, *messages]

    last_user = next(
        (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"),
        "",
    )
    print(f"[chat] user: {last_user[:120]}", flush=True)

    async def stream():
        nonlocal messages
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                for _ in range(MAX_TOOL_ROUNDS + 1):
                    payload = {"model": model, "messages": messages, "stream": True}
                    if use_tools:
                        payload["tools"] = TOOLS

                    assistant_content = ""
                    tool_calls: list = []

                    async with client.stream(
                        "POST", f"{OLLAMA_URL}/api/chat", json=payload
                    ) as r:
                        async for line in r.aiter_lines():
                            if not line:
                                continue
                            try:
                                obj = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            msg = obj.get("message") or {}
                            delta = msg.get("content", "")
                            if delta:
                                assistant_content += delta
                                yield f"data: {json.dumps({'delta': delta})}\n\n"
                            if msg.get("tool_calls"):
                                tool_calls.extend(msg["tool_calls"])
                            if obj.get("done"):
                                break

                    if not tool_calls:
                        if assistant_content:
                            print(
                                f"[chat] assistant: {assistant_content[:200]}",
                                flush=True,
                            )
                        yield "data: [DONE]\n\n"
                        return

                    messages = messages + [{
                        "role": "assistant",
                        "content": assistant_content,
                        "tool_calls": tool_calls,
                    }]

                    for tc in tool_calls:
                        fn = tc.get("function") or {}
                        name = fn.get("name", "")
                        args = fn.get("arguments") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except json.JSONDecodeError:
                                args = {}
                        try:
                            result = await dispatch_tool(name, args)
                            result_str = (
                                result if isinstance(result, str)
                                else json.dumps(result)
                            )
                            print(f"[tool] {name}({args}) = {result_str}", flush=True)
                        except BridgeError as exc:
                            result_str = json.dumps({"error": str(exc)})
                            print(f"[tool] {name}({args}) ERROR {exc}", flush=True)
                        yield (
                            "data: "
                            + json.dumps({
                                "tool": {"name": name, "args": args, "result": result_str}
                            })
                            + "\n\n"
                        )
                        messages = messages + [{
                            "role": "tool",
                            "name": name,
                            "content": result_str,
                        }]

                yield "data: [DONE]\n\n"
        except httpx.HTTPError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/bridge/health")
async def bridge_health():
    return {"connected": bridge.connected, "port": bridge.port}


@app.post("/api/bridge/call")
async def bridge_call(request: Request):
    body = await request.json()
    method = body.get("method")
    args = body.get("args", [])
    if not isinstance(method, str):
        raise HTTPException(status_code=400, detail="method required")
    if not isinstance(args, list):
        raise HTTPException(status_code=400, detail="args must be array")
    try:
        result = await bridge.call(method, args)
    except BridgeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"result": result}


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
