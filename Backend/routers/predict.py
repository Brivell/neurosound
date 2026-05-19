import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.engine import get_db
from database.models import Prediction
from schemas.prediction import PredictionResponse
from services import spectrogram_service, yamnet_service

settings = get_settings()
logger   = logging.getLogger(__name__)
router   = APIRouter()


def _registry(request: Request) -> dict:
    from main import registry
    return registry


@router.post("/predict/wav", response_model=PredictionResponse)
async def predict_wav(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files accepted")

    content   = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large — max {settings.max_file_size_mb}MB",
        )

    reg = _registry(request)
    yamnet_hub = reg.get("yamnet_hub")
    yamnet     = reg.get("yamnet")
    if not yamnet_hub or not yamnet:
        raise HTTPException(status_code=503, detail="YAMNet model not loaded")

    try:
        result = yamnet_service.predict(content, yamnet_hub, yamnet)
    except Exception as e:
        logger.error(f"YAMNet inference error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference failed")

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
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.lower().endswith(".png"):
        raise HTTPException(status_code=400, detail="Only .png files accepted")

    content   = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large — max {settings.max_file_size_mb}MB",
        )

    reg = _registry(request)
    spectro_model = reg.get("spectrogram")
    if not spectro_model:
        raise HTTPException(status_code=503, detail="EfficientNetB3 model not loaded")

    try:
        result = spectrogram_service.predict(content, spectro_model)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"EfficientNetB3 inference error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference failed")

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
