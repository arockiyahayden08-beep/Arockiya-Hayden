from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    yield


settings = get_settings()
app = FastAPI(
    title="ComicCraft — AI Comic Story Creator",
    description="Generate five-panel cartoon comics with Gemini and Hugging Face.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
# Friendly aliases used by the generated pages and JSON API.
app.mount("/panels", StaticFiles(directory=str(settings.panels_dir)), name="panels")
app.mount("/exports", StaticFiles(directory=str(settings.exports_dir)), name="exports")
app.include_router(router)

@app.get("/health")
async def health():
    from app.services.health import status
    return status(settings)
