import json
import os
import uuid
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
CHATS_FILE = DATA_DIR / "chats.json"

DATA_DIR.mkdir(exist_ok=True)
if not CHATS_FILE.exists():
    CHATS_FILE.write_text("[]", encoding="utf-8")

AI_BACKEND = os.getenv("AI_BACKEND", "llama").lower()
LLAMA_BASE_URL = os.getenv("LLAMA_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("DARCK_MODEL", "local")
PORT = int(os.getenv("PORT", "8000"))

app = FastAPI(title="Darck ChatGPT V2")
app.mount("/static", StaticFiles(directory=str(BASE)), name="static")


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
    tmp.write_text(json.dumps(chats, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CHATS_FILE)


@app.get("/")
async def index():
    return FileResponse(BASE / "index.html")


@app.get("/api/health")
async def health():
    url = OLLAMA_BASE_URL if AI_BACKEND == "ollama" else LLAMA_BASE_URL
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            if AI_BACKEND == "ollama":
                response = await client.get(f"{url}/api/tags")
            else:
                response = await client.get(f"{url}/health")
        return {"ok": response.status_code < 400, "backend": AI_BACKEND, "url": url}
    except Exception as exc:
        return {"ok": False, "backend": AI_BACKEND, "url": url, "error": str(exc)}


@app.get("/api/models")
async def models():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            if AI_BACKEND == "ollama":
                response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                data = response.json()
                return {"models": [{"name": x.get("name", "")} for x in data.get("models", [])]}
            response = await client.get(f"{LLAMA_BASE_URL}/v1/models")
            data = response.json()
            return {"models": [{"name": x.get("id", DEFAULT_MODEL)} for x in data.get("data", [])]}
    except Exception:
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
    write_chats([x for x in read_chats() if x.get("id") != chat_id])
    return {"ok": True}


async def call_ollama(request: ChatRequest):
    payload = {
        "model": request.model or os.getenv("DARCK_MODEL", "llama3.2:1b"),
        "messages": request.messages,
        "stream": False,
        "options": {
            "temperature": request.temperature,
            "num_predict": request.max_tokens,
        },
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return {"message": {"role": "assistant", "content": data.get("message", {}).get("content", "")}}


async def call_llama(request: ChatRequest):
    payload = {
        "model": request.model or DEFAULT_MODEL,
        "messages": request.messages,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(f"{LLAMA_BASE_URL}/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"message": {"role": "assistant", "content": content}}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if AI_BACKEND == "ollama":
        return await call_ollama(request)
    return await call_llama(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
