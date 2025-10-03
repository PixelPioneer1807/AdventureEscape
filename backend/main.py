from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from routers import story, job
from routes import auth, saves
from db.database import create_tables
from routes.analytics import router as analytics_router
# Import all models to ensure they're registered with SQLAlchemy
from models.user import User
from models.story import Story, StoryNode  
from models.job import StoryJob
from models.save_game import SaveGame, UserStoryProgress

create_tables()

# --- logging setup (add near top of main.py) ---
import logging
from logging.config import dictConfig

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"default": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default", "level": "DEBUG"}},
    "loggers": {"app": {"handlers": ["console"], "level": "DEBUG", "propagate": False}},
    "root": {"handlers": ["console"], "level": "INFO"},
})
# --- end logging setup ---

app = FastAPI(
    title="Choose Your Own Adventure Game API",
    description="api to generate cool stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(saves.router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)

# --- CRITICAL: Static Files Route to serve images to the frontend ---
# This mounts /static/ to serve from generated_images directory
app.mount("/static", StaticFiles(directory="generated_images"), name="static")
# --- END STATIC MOUNT ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)