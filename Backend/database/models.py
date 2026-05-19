from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from database.engine import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp  = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    filename   = Column(String(255), nullable=False)
    input_type = Column(String(20),  nullable=False)   # 'wav' | 'spectrogram'
    model_used = Column(String(50),  nullable=False)   # 'yamnet' | 'efficientnetb3'
    prediction = Column(String(100), nullable=False)
    confidence = Column(Float,       nullable=False)
    top5       = Column(Text,        nullable=False)   # JSON string
