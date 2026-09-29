from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router


# Make sure required directories exist.
Path("static/panels").mkdir(
    parents=True,
    exist_ok=True,
)

Path("static/exports").mkdir(
    parents=True,
    exist_ok=True,
)


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered five-panel comic story creator."
    ),
    version="1.0.0",
)


# Serve CSS, JavaScript, generated images and other
# static files.
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# Register application routes.
app.include_router(router)


@app.get("/health")
async def health():
    """
    Simple health-check endpoint.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "demo_mode": settings.demo_mode,
    }