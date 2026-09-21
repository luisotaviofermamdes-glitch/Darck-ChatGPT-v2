import json
import os
import uuid
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_NAME = "Darck ChatGPT"
BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
STATIC_DIR = BASE / "static"
CHATS_FILE = DATA_DIR / "chats.json"

DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

if not CHATS_FILE.exists():
    CHATS_FILE.write_text("[]", encoding="utf-8")

LLAMA_BASE_URL = os.getenv("LLAMA_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
DEFAULT_MODEL = os.getenv("DARCK_MODEL", "local")

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ChatRequest(BaseModel):
    messages: list[dict]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512


def read_chats():
    try:
        return json.loads(CHATS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def write_chats(chats):
    tmp = CHATS_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(chats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(CHATS_FILE)


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{LLAMA_BASE_URL}/health")
        return {
            "ok": response.status_code == 200,
            "backend": LLAMA_BASE_URL,
        }
    except Exception as exc:
        return {
            "ok": False,
            "backend": LLAMA_BASE_URL,
            "error": str(exc),
        }


@app.get("/api/models")
async def models():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{LLAMA_BASE_URL}/v1/models")
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                return {
                    "models": [
                        {"name": item.get("id", DEFAULT_MODEL)}
                        for item in items
                    ]
                }
    except Exception:
        pass

    return {"models": [{"name": DEFAULT_MODEL}]}


@app.get("/api/chats")
async def get_chats():
    return read_chats()


@app.post("/api/chats")
async def save_chat(chat: dict):
    chats = read_chats()

    if not chat.get("id"):
        chat["id"] = str(uuid.uuid4())

    chats = [item for item in chats if item.get("id") != chat["id"]]
    chats.insert(0, chat)

    write_chats(chats[:100])
    return chat


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    chats = [item for item in read_chats() if item.get("id") != chat_id]
    write_chats(chats)
    return {"ok": True}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    payload = {
        "model": request.model or DEFAULT_MODEL,
        "messages": request.messages,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": True,
    }

    async def stream():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{LLAMA_BASE_URL}/v1/chat/completions",
                    json=payload,
                ) as response:

                    if response.status_code >= 400:
                        yield (
                            "data: "
                            + json.dumps(
                                {
                                    "error": (
                                        f"Motor local HTTP "
                                        f"{response.status_code}"
                                    )
                                }
                            )
                            + "\n\n"
                        )
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            yield line.strip() + "\n\n"

        except Exception as exc:
            yield (
                "data: "
                + json.dumps({"error": str(exc)})
                + "\n\n"
            )

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )
