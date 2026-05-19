from functools import lru_cache
from pydantic_settings import BaseSettings


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
