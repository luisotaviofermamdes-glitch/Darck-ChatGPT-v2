import json
import os
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_NAME = "Darck ChatGPT"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHATS_FILE = DATA_DIR / "chats.json"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("DARCK_MODEL", "")

DATA_DIR.mkdir(exist_ok=True)
if not CHATS_FILE.exists():
    CHATS_FILE.write_text("[]", encoding="utf-8")

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str
    chat_id: str | None = None


class SaveChatRequest(BaseModel):
    id: str | None = None
    title: str = "Novo chat"
    messages: list[dict] = []


def load_chats():
    try:
        return json.loads(CHATS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_chats(chats):
    CHATS_FILE.write_text(json.dumps(chats, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        return {"ok": response.is_success, "ollama": OLLAMA_BASE_URL}
    except Exception as exc:
        return {"ok": False, "ollama": OLLAMA_BASE_URL, "error": str(exc)}


@app.get("/api/models")
async def models():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
        data = response.json()
        names = [m.get("name") for m in data.get("models", []) if m.get("name")]
        return {"models": names, "default": DEFAULT_MODEL or (names[0] if names else "")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Não foi possível acessar o Ollama: {exc}")


@app.get("/api/chats")
async def get_chats():
    return load_chats()


@app.post("/api/chats")
async def save_chat(payload: SaveChatRequest):
    chats = load_chats()
    chat_id = payload.id or str(uuid.uuid4())
    item = {
        "id": chat_id,
        "title": payload.title[:100],
        "messages": payload.messages,
    }
    chats = [c for c in chats if c.get("id") != chat_id]
    chats.insert(0, item)
    save_chats(chats[:100])
    return item


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    chats = [c for c in load_chats() if c.get("id") != chat_id]
    save_chats(chats)
    return {"ok": True}


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if not payload.model:
        raise HTTPException(status_code=400, detail="Selecione um modelo.")
    if not payload.messages:
        raise HTTPException(status_code=400, detail="A conversa está vazia.")

    async def stream():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json={
                        "model": payload.model,
                        "messages": payload.messages,
                        "stream": True,
                    },
                ) as response:
                    if response.status_code >= 400:
                        body = await response.aread()
                        yield json.dumps({"error": body.decode("utf-8", errors="replace")}) + "\n"
                        return
                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n"
        except Exception as exc:
            yield json.dumps({"error": str(exc)}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
