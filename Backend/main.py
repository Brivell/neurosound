import logging
import logging.config
from contextlib import asynccontextmanager

import tensorflow as tf
import tensorflow_hub as hub
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database.engine import init_db
from middleware.logging import LoggingMiddleware
from routers import health, history, predict

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Global model registry ────────────────────────────────────────────────────
registry: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models once at startup — never per request."""
    logger.info("🚀 Starting NeuroSound API...")

    await init_db()

    logger.info("Loading YAMNet hub model...")
    registry["yamnet_hub"] = hub.load(settings.yamnet_hub_url)

    logger.info(f"Loading YAMNet head: {settings.yamnet_model_path}")
    registry["yamnet"] = tf.keras.models.load_model(settings.yamnet_model_path)

    logger.info(f"Loading EfficientNetB3: {settings.spectrogram_model_path}")
    registry["spectrogram"] = tf.keras.models.load_model(
        settings.spectrogram_model_path
    )

    logger.info("✅ All models loaded — API ready")
    yield

    registry.clear()
    logger.info("🛑 API shutdown — models cleared")


# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NeuroSound API",
    description="AI-powered acoustic classification — EfficientNetB3 + YAMNet",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS must be before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(predict.router, prefix="/api", tags=["Prediction"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(health.router,  prefix="/api", tags=["Health"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Unexpected error occurred"},
    )
