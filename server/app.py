import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from bridge import BridgeError, bridge

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
    except Exception:
        pass
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
    messages = body.get("messages", [])
    model = body.get("model", DEFAULT_MODEL)

    if SYSTEM_PROMPT and not (messages and messages[0].get("role") == "system"):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

    payload = {"model": model, "messages": messages, "stream": True}

    async def stream():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
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
                        delta = obj.get("message", {}).get("content", "")
                        if delta:
                            yield f"data: {json.dumps({'delta': delta})}\n\n"
                        if obj.get("done"):
                            yield "data: [DONE]\n\n"
                            return
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
    params = body.get("params") or {}
    if not isinstance(method, str):
        raise HTTPException(status_code=400, detail="method required")
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="params must be object")
    try:
        result = await bridge.call(method, params)
    except BridgeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"result": result}


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
