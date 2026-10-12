import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .api.health import router as health_router
from .api.sessions import router as sessions_router
from .api.ws_voice import router as ws_voice_router

STATIC_DIR = Path(__file__).parent / "static"

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.time() - start:.3f}s"
    return response


app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(ws_voice_router)


@app.get("/")
async def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/text")
async def serve_text():
    return FileResponse(STATIC_DIR / "text.html")


@app.get("/chat")
async def serve_chat():
    return FileResponse(STATIC_DIR / "chat.html")


@app.get("/voice")
async def serve_voice():
    return FileResponse(STATIC_DIR / "voice.html")


@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse(STATIC_DIR / "manifest.json")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
