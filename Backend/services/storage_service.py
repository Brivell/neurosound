import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Prediction

logger = logging.getLogger(__name__)


async def save_prediction(
    db: AsyncSession,
    *,
    filename: str,
    input_type: str,
    model_used: str,
    prediction: str,
    confidence: float,
    top5: list,
    timestamp: datetime | None = None,
) -> Prediction:
    """Persist an inference result and return the ORM row."""
    ts = timestamp or datetime.now(timezone.utc)
    row = Prediction(
        filename   = filename,
        input_type = input_type,
        model_used = model_used,
        prediction = prediction,
        confidence = confidence,
        top5       = json.dumps(top5),
        timestamp  = ts,
    )
    db.add(row)
    await db.flush()   # populate row.id without closing the session
    logger.debug(f"Saved prediction id={row.id} [{model_used}] {prediction} {confidence:.3f}")
    return row
