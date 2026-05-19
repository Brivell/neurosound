# CLAUDE.md — NeuroSound Backend (Elite)

## Always Do First
- Read global `../CLAUDE_global.md` for API contract, DB schema, ESC-50 labels.
- Models load ONCE at startup via lifespan — never per request.
- Never expose raw TensorFlow, SQLAlchemy, or Python errors to frontend.
- Always validate file type + size before any processing.
- Run `uvicorn main:app --reload --port 8000` from `Backend/` directory.

---

## Stack
```
Framework   : FastAPI 0.110+
ML          : TensorFlow 2.15 + tensorflow-hub 0.16
Audio       : librosa 0.10 + soundfile
Vision      : opencv-python-headless
Database    : SQLite + SQLAlchemy 2.0 (async)
Server      : Uvicorn + Gunicorn (prod)
Validation  : Pydantic v2
Logging     : Python logging + structlog
Testing     : pytest + httpx
Python      : 3.10+
```

---

## Project Structure
```
Backend/
├── CLAUDE.md
├── main.py                      ← FastAPI app entry point
├── config.py                    ← Settings via pydantic-settings
├── dependencies.py              ← Shared FastAPI dependencies
├── routers/
│   ├── __init__.py
│   ├── predict.py               ← POST /api/predict/wav + /spectrogram
│   ├── history.py               ← GET/DELETE /api/history
│   └── health.py                ← GET /api/health
├── services/
│   ├── __init__.py
│   ├── yamnet_service.py        ← WAV → YAMNet embeddings → prediction
│   ├── spectrogram_service.py   ← PNG → EfficientNetB3 → prediction
│   └── storage_service.py       ← DB write/read helpers
├── database/
│   ├── __init__.py
│   ├── engine.py                ← SQLAlchemy async engine + session
│   └── models.py                ← ORM models
├── schemas/
│   ├── __init__.py
│   ├── prediction.py            ← Pydantic request/response schemas
│   └── history.py               ← History response schemas
├── middleware/
│   ├── __init__.py
│   └── logging.py               ← Request/response logging middleware
├── Models/
│   ├── spectrogram_model.keras  ← EfficientNetB3 93.34%
│   └── yamnet_esc50.keras       ← YAMNet 88.5%
├── tests/
│   ├── __init__.py
│   ├── test_predict.py
│   └── test_history.py
├── requirements.txt
├── requirements-dev.txt
├── .env
├── .env.example
└── Dockerfile
```

---

## Environment Variables

### .env (never commit this file)
```
SPECTROGRAM_MODEL_PATH=./Models/spectrogram_model.keras
YAMNET_MODEL_PATH=./Models/yamnet_esc50.keras
YAMNET_HUB_URL=https://tfhub.dev/google/yamnet/1
DATABASE_URL=sqlite+aiosqlite:///./neurosound.db
FRONTEND_ORIGIN=http://localhost:3000
MAX_FILE_SIZE_MB=10
IMAGE_SIZE=300
SAMPLE_RATE=16000
AUDIO_DURATION=5
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### .env.example (commit this)
```
SPECTROGRAM_MODEL_PATH=./Models/spectrogram_model.keras
YAMNET_MODEL_PATH=./Models/yamnet_esc50.keras
YAMNET_HUB_URL=https://tfhub.dev/google/yamnet/1
DATABASE_URL=sqlite+aiosqlite:///./neurosound.db
FRONTEND_ORIGIN=http://localhost:3000
MAX_FILE_SIZE_MB=10
IMAGE_SIZE=300
SAMPLE_RATE=16000
AUDIO_DURATION=5
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## config.py — Settings
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    spectrogram_model_path: str = "./Models/spectrogram_model.keras"
    yamnet_model_path: str      = "./Models/yamnet_esc50.keras"
    yamnet_hub_url: str         = "https://tfhub.dev/google/yamnet/1"
    database_url: str           = "sqlite+aiosqlite:///./neurosound.db"
    frontend_origin: str        = "http://localhost:3000"
    max_file_size_mb: int       = 10
    image_size: int             = 300
    sample_rate: int            = 16000
    audio_duration: int         = 5
    log_level: str              = "INFO"
    environment: str            = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## main.py — Entry Point
```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import tensorflow as tf
import tensorflow_hub as hub

from config import get_settings
from database.engine import init_db
from routers import predict, history, health
from middleware.logging import LoggingMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)

# ── Global model registry ────────────────────────────────────────────────────
registry: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models once at startup — never per request."""
    logger.info("🚀 Starting NeuroSound API...")

    # Init database
    await init_db()

    # Load YAMNet hub model (for embedding extraction)
    logger.info("Loading YAMNet hub model...")
    registry["yamnet_hub"] = hub.load(settings.yamnet_hub_url)

    # Load YAMNet classification head
    logger.info(f"Loading YAMNet head: {settings.yamnet_model_path}")
    registry["yamnet"] = tf.keras.models.load_model(settings.yamnet_model_path)

    # Load EfficientNetB3 spectrogram model
    logger.info(f"Loading EfficientNetB3: {settings.spectrogram_model_path}")
    registry["spectrogram"] = tf.keras.models.load_model(
        settings.spectrogram_model_path
    )

    logger.info("✅ All models loaded — API ready")
    yield

    # Cleanup
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

# ── CORS — must be before routers ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# ── Logging middleware ────────────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(predict.router,  prefix="/api", tags=["Prediction"])
app.include_router(history.router,  prefix="/api", tags=["History"])
app.include_router(health.router,   prefix="/api", tags=["Health"])

# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Unexpected error occurred"}
    )
```

---

## ESC-50 Labels (exact order — index = target class)
```python
ESC50_LABELS = [
    "dog", "sheep", "hen", "cow", "insects", "frog", "pig", "rooster",
    "cat", "crow", "chirping_birds", "rain", "wind", "sea_waves",
    "crickets", "thunderstorm", "pouring_water", "toilet_flush",
    "crackling_fire", "water_drops", "brushing_teeth", "laughing",
    "crying_baby", "clapping", "footsteps", "drinking_sipping",
    "snoring", "coughing", "sneezing", "breathing", "vacuum_cleaner",
    "mouse_click", "washing_machine", "clock_tick", "glass_breaking",
    "door_wood_creaks", "keyboard_typing", "clock_alarm", "can_opening",
    "door_wood_knock", "chainsaw", "airplane", "train", "engine",
    "siren", "hand_saw", "helicopter", "car_horn", "church_bells",
    "fireworks"
]
```

---

## Schemas — Pydantic v2

### schemas/prediction.py
```python
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Top5Item(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float = Field(ge=0.0, le=1.0)
    top5: List[Top5Item]
    model: str
    filename: str
    input_type: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    error: str
    detail: str
```

### schemas/history.py
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

class HistoryItem(BaseModel):
    id: int
    timestamp: datetime
    filename: str
    input_type: str
    model_used: str
    prediction: str
    confidence: float
    top5: List[dict]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            timestamp=obj.timestamp,
            filename=obj.filename,
            input_type=obj.input_type,
            model_used=obj.model_used,
            prediction=obj.prediction,
            confidence=obj.confidence,
            top5=json.loads(obj.top5) if isinstance(obj.top5, str) else obj.top5
        )

class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
```

---

## Database — Async SQLAlchemy

### database/engine.py
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        from database.models import Prediction
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """FastAPI dependency — yields async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### database/models.py
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database.engine import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp  = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    filename   = Column(String(255), nullable=False)
    input_type = Column(String(20), nullable=False)   # 'wav' | 'spectrogram'
    model_used = Column(String(50), nullable=False)   # 'yamnet' | 'efficientnetb3'
    prediction = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    top5       = Column(Text, nullable=False)          # JSON string
```

---

## Services

### services/yamnet_service.py
```python
import io
import json
import logging
import numpy as np
import tensorflow as tf
import librosa
import soundfile as sf
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

ESC50_LABELS = [
    "dog", "sheep", "hen", "cow", "insects", "frog", "pig", "rooster",
    "cat", "crow", "chirping_birds", "rain", "wind", "sea_waves",
    "crickets", "thunderstorm", "pouring_water", "toilet_flush",
    "crackling_fire", "water_drops", "brushing_teeth", "laughing",
    "crying_baby", "clapping", "footsteps", "drinking_sipping",
    "snoring", "coughing", "sneezing", "breathing", "vacuum_cleaner",
    "mouse_click", "washing_machine", "clock_tick", "glass_breaking",
    "door_wood_creaks", "keyboard_typing", "clock_alarm", "can_opening",
    "door_wood_knock", "chainsaw", "airplane", "train", "engine",
    "siren", "hand_saw", "helicopter", "car_horn", "church_bells",
    "fireworks"
]

def preprocess_wav(file_bytes: bytes) -> tf.Tensor:
    """Load WAV bytes → mono 16kHz float32 tensor, fixed duration."""
    target_sr  = settings.sample_rate
    target_len = target_sr * settings.audio_duration

    try:
        y, sr = sf.read(io.BytesIO(file_bytes))
    except Exception:
        y, sr = librosa.load(io.BytesIO(file_bytes),
                             sr=target_sr, mono=True,
                             duration=settings.audio_duration)
        return tf.constant(y, dtype=tf.float32)

    # Stereo → mono
    if y.ndim > 1:
        y = y.mean(axis=1)

    # Resample if needed
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

    # Pad or truncate
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]

    return tf.constant(y.astype(np.float32), dtype=tf.float32)


def predict(file_bytes: bytes, yamnet_hub, model) -> dict:
    """Full YAMNet inference pipeline."""
    wav_tensor = preprocess_wav(file_bytes)

    # Extract embeddings via YAMNet hub
    _, embeddings, _ = yamnet_hub(wav_tensor)
    emb = tf.reduce_mean(embeddings, axis=0).numpy()
    emb = np.expand_dims(emb, axis=0)

    # Classification head
    probs    = model.predict(emb, verbose=0)[0]
    top5_idx = np.argsort(probs)[::-1][:5]
    pred_idx = int(np.argmax(probs))

    return {
        "prediction": ESC50_LABELS[pred_idx],
        "confidence": float(probs[pred_idx]),
        "top5": [
            {"label": ESC50_LABELS[i], "confidence": float(probs[i])}
            for i in top5_idx
        ],
        "model": "yamnet"
    }
```

### services/spectrogram_service.py
```python
import io
import logging
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

ESC50_LABELS = [
    "dog", "sheep", "hen", "cow", "insects", "frog", "pig", "rooster",
    "cat", "crow", "chirping_birds", "rain", "wind", "sea_waves",
    "crickets", "thunderstorm", "pouring_water", "toilet_flush",
    "crackling_fire", "water_drops", "brushing_teeth", "laughing",
    "crying_baby", "clapping", "footsteps", "drinking_sipping",
    "snoring", "coughing", "sneezing", "breathing", "vacuum_cleaner",
    "mouse_click", "washing_machine", "clock_tick", "glass_breaking",
    "door_wood_creaks", "keyboard_typing", "clock_alarm", "can_opening",
    "door_wood_knock", "chainsaw", "airplane", "train", "engine",
    "siren", "hand_saw", "helicopter", "car_horn", "church_bells",
    "fireworks"
]

def preprocess_png(file_bytes: bytes) -> np.ndarray:
    """Decode PNG bytes → EfficientNetB3 input array (1, 300, 300, 3)."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image — invalid PNG file")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (settings.image_size, settings.image_size))
    img = preprocess_input(img.astype(np.float32))
    return np.expand_dims(img, axis=0)


def predict(file_bytes: bytes, model) -> dict:
    """Full EfficientNetB3 inference pipeline."""
    img_array = preprocess_png(file_bytes)
    probs     = model.predict(img_array, verbose=0)[0]
    top5_idx  = np.argsort(probs)[::-1][:5]
    pred_idx  = int(np.argmax(probs))

    return {
        "prediction": ESC50_LABELS[pred_idx],
        "confidence": float(probs[pred_idx]),
        "top5": [
            {"label": ESC50_LABELS[i], "confidence": float(probs[i])}
            for i in top5_idx
        ],
        "model": "efficientnetb3"
    }
```

---

## Routers

### routers/predict.py
```python
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.engine import get_db
from database.models import Prediction
from services import yamnet_service, spectrogram_service
from schemas.prediction import PredictionResponse

settings = get_settings()
logger   = logging.getLogger(__name__)
router   = APIRouter()

def get_registry(request: Request) -> dict:
    return request.app.state.registry if hasattr(request.app.state, "registry") \
        else request.app.extra.get("registry", {})


@router.post("/predict/wav", response_model=PredictionResponse)
async def predict_wav(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Validate file type
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files accepted")

    # Validate file size
    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large — max {settings.max_file_size_mb}MB"
        )

    # Get models from registry
    from main import registry
    yamnet_hub = registry.get("yamnet_hub")
    yamnet     = registry.get("yamnet")
    if not yamnet_hub or not yamnet:
        raise HTTPException(status_code=503, detail="YAMNet model not loaded")

    # Predict
    try:
        result = yamnet_service.predict(content, yamnet_hub, yamnet)
    except Exception as e:
        logger.error(f"YAMNet inference error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference failed")

    # Persist to DB
    now = datetime.now(timezone.utc)
    db.add(Prediction(
        filename   = file.filename,
        input_type = "wav",
        model_used = "yamnet",
        prediction = result["prediction"],
        confidence = result["confidence"],
        top5       = json.dumps(result["top5"]),
        timestamp  = now,
    ))

    return PredictionResponse(
        **result,
        filename   = file.filename,
        input_type = "wav",
        timestamp  = now,
    )


@router.post("/predict/spectrogram", response_model=PredictionResponse)
async def predict_spectrogram(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Validate file type
    if not file.filename.lower().endswith(".png"):
        raise HTTPException(status_code=400, detail="Only .png files accepted")

    # Validate file size
    content   = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large — max {settings.max_file_size_mb}MB"
        )

    # Get model from registry
    from main import registry
    spectro_model = registry.get("spectrogram")
    if not spectro_model:
        raise HTTPException(status_code=503, detail="EfficientNetB3 model not loaded")

    # Predict
    try:
        result = spectrogram_service.predict(content, spectro_model)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"EfficientNetB3 inference error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference failed")

    # Persist to DB
    now = datetime.now(timezone.utc)
    db.add(Prediction(
        filename   = file.filename,
        input_type = "spectrogram",
        model_used = "efficientnetb3",
        prediction = result["prediction"],
        confidence = result["confidence"],
        top5       = json.dumps(result["top5"]),
        timestamp  = now,
    ))

    return PredictionResponse(
        **result,
        filename   = file.filename,
        input_type = "spectrogram",
        timestamp  = now,
    )
```

### routers/history.py
```python
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from database.engine import get_db
from database.models import Prediction
from schemas.history import HistoryItem, HistoryResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, le=200),
    input_type: str = Query(default=None)  # optional filter: 'wav' | 'spectrogram'
):
    query = select(Prediction).order_by(Prediction.timestamp.desc())
    if input_type in ("wav", "spectrogram"):
        query = query.where(Prediction.input_type == input_type)
    query = query.limit(limit)

    result = await db.execute(query)
    rows   = result.scalars().all()

    count_q = select(func.count()).select_from(Prediction)
    total   = (await db.execute(count_q)).scalar()

    return HistoryResponse(
        items=[HistoryItem.from_orm(r) for r in rows],
        total=total
    )


@router.delete("/history/{prediction_id}")
async def delete_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Prediction not found")

    await db.execute(delete(Prediction).where(Prediction.id == prediction_id))
    return {"success": True, "deleted_id": prediction_id}
```

### routers/health.py
```python
from fastapi import APIRouter
from main import registry

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "models_loaded": {
            "yamnet_hub":   "yamnet_hub"   in registry and registry["yamnet_hub"]   is not None,
            "yamnet":       "yamnet"       in registry and registry["yamnet"]       is not None,
            "spectrogram":  "spectrogram"  in registry and registry["spectrogram"]  is not None,
        }
    }
```

---

## Middleware

### middleware/logging.py
```python
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} [{duration}ms]"
        )
        return response
```

---

## Requirements

### requirements.txt
```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
tensorflow>=2.15.0
tensorflow-hub>=0.16.0
librosa>=0.10.0
soundfile>=0.12.0
opencv-python-headless>=4.9.0
numpy>=1.26.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
python-multipart>=0.0.9
python-dotenv>=1.0.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
```

### requirements-dev.txt
```
pytest>=8.0.0
httpx>=0.27.0
pytest-asyncio>=0.23.0
```

---

## Run Commands
```bash
# Install
pip install -r requirements.txt

# Development (from Backend/ directory)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Interactive API docs
http://localhost:8000/api/docs

# Health check
curl http://localhost:8000/api/health

# Test WAV prediction
curl -X POST http://localhost:8000/api/predict/wav \
  -F "file=@test.wav"

# Test PNG prediction
curl -X POST http://localhost:8000/api/predict/spectrogram \
  -F "file=@test.png"
```

---

## Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# System deps for librosa + opencv
RUN apt-get update && apt-get install -y \
    libsndfile1 libgomp1 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Hard Rules
- NEVER load models inside a request handler — always use lifespan + registry dict
- NEVER return raw TensorFlow, NumPy, or SQLAlchemy errors to frontend
- ALWAYS validate file extension AND file size before any processing
- ALWAYS save prediction to DB after successful inference
- NEVER use synchronous file I/O in async endpoints
- CORS middleware MUST be declared before all routers
- ESC50_LABELS index MUST match training target order exactly
- Use `aiosqlite` driver for async SQLite — never synchronous sqlite3
- Registry dict in main.py is the single source of truth for loaded models
- Health endpoint MUST reflect real model load status — never hardcode "true"
