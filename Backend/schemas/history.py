import json
from datetime import datetime
from typing import List

from pydantic import BaseModel


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
            top5=json.loads(obj.top5) if isinstance(obj.top5, str) else obj.top5,
        )


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
