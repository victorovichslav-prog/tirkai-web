# -*- coding: utf-8 -*-
"""
TirkAI Web Server — FastAPI + Jinja2
"""

import os, asyncio, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tirkai import TirkAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TirkAI-Server")

# Глобальная переменная для модели
tirkai = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tirkai
    logger.info("🚀 Loading TirkAI...")
    tirkai = TirkAI(knowledge_path="knowledge.txt")
    logger.info("✅ TirkAI ready!")
    yield
    logger.info("👋 Shutting down...")

app = FastAPI(title="TirkAI", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ═══════════════════════════════════════════════════════════════
# РОУТЫ
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def api_chat(question: str = Form(...)):
    if not tirkai:
        return JSONResponse({"error": "Model not loaded"}, status_code=503)

    try:
        result = tirkai.ask(question)
        return JSONResponse({
            "answer": result["answer"],
            "context_preview": result["context"][:200] + "..." if len(result["context"]) > 200 else result["context"]
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/health")
async def health():
    return {"status": "ok", "model_loaded": tirkai is not None}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
