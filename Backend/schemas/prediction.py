from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


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
