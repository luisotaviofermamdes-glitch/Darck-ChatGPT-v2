import json, os, uuid
from pathlib import Path
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP= "Darck ChatGPT"
BASE=Path(__file__).resolve().parent
DATA=BASE/"data"; DATA.mkdir(exist_ok=True)
CHATS=DATA/"chats.json"
if not CHATS.exists(): CHATS.write_text("[]",encoding="utf-8")

LLAMA_URL=os.getenv("LLAMA_BASE_URL","http://127.0.0.1:8080")
MODEL=os.getenv("DARCK_MODEL","qwen2.5-0.5b-instruct")
app=FastAPI(title=APP)
app.mount("/static",StaticFiles(directory=str(BASE/"static")),name="static")

class ChatReq(BaseModel):
    messages:list[dict]
    model:Optional[str]=None
    temperature:float=0.7

def read_chats():
    try:return json.loads(CHATS.read_text(encoding="utf-8"))
    except:return []
def write_chats(x): CHATS.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")

@app.get("/")
def index(): return FileResponse(BASE/"static/index.html")

@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r=await c.get(f"{LLAMA_URL}/health")
            return {"ok":r.status_code==200,"backend":LLAMA_URL}
    except Exception as e:return {"ok":False,"backend":LLAMA_URL,"error":str(e)}

@app.get("/api/models")
async def models():
    return {"models":[{"name":MODEL}]}

@app.get("/api/chats")
def chats(): return read_chats()

@app.post("/api/chats")
def save_chat(chat:dict):
    items=read_chats()
    if not chat.get("id"): chat["id"]=str(uuid.uuid4())
    items=[x for x in items if x.get("id")!=chat["id"]]
    items.insert(0,chat); write_chats(items[:100])
    return chat

@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id:str):
    write_chats([x for x in read_chats() if x.get("id")!=chat_id])
    return {"ok":True}

@app.post("/api/chat")
async def chat(req:ChatReq):
    payload={"model":req.model or MODEL,"messages":req.messages,"temperature":req.temperature,"stream":True}
    async def gen():
        try:
            async with httpx.AsyncClient(timeout=None) as c:
                async with c.stream("POST",f"{LLAMA_URL}/v1/chat/completions",json=payload) as r:
                    if r.status_code>=400:
                        yield f"data: {{\"error\":\"backend HTTP {r.status_code}\"}}\n\n"; return
                    async for line in r.aiter_lines():
                        if line.startswith("data: "): yield line+"\n\n"
        except Exception as e:
            yield f"data: {{\"error\":{json.dumps(str(e))}}}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream")

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=int(os.getenv("PORT","8000")))
