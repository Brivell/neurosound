import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_db
from database.models import Prediction
from schemas.history import HistoryItem, HistoryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, le=200),
    input_type: str | None = Query(default=None),
):
    query = select(Prediction).order_by(Prediction.timestamp.desc())
    if input_type in ("wav", "spectrogram"):
        query = query.where(Prediction.input_type == input_type)
    query = query.limit(limit)

    rows  = (await db.execute(query)).scalars().all()
    total = (await db.execute(select(func.count()).select_from(Prediction))).scalar()

    return HistoryResponse(
        items=[HistoryItem.from_orm(r) for r in rows],
        total=total,
    )


@router.delete("/history/{prediction_id}")
async def delete_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
):
    row = (
        await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    ).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="Prediction not found")

    await db.execute(delete(Prediction).where(Prediction.id == prediction_id))
    return {"success": True, "deleted_id": prediction_id}
