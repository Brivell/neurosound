import io
import wave
import struct

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import app


def _make_wav_bytes(duration_s: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generate a minimal silent WAV in memory."""
    num_samples = int(sample_rate * duration_s)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{num_samples}h", *([0] * num_samples)))
    return buf.getvalue()


@pytest.fixture
def wav_bytes():
    return _make_wav_bytes()


@pytest.mark.asyncio
async def test_predict_wav_missing_model(wav_bytes):
    """Should return 503 when registry is empty (no models loaded)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/predict/wav",
            files={"file": ("test.wav", wav_bytes, "audio/wav")},
        )
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_predict_wav_wrong_extension():
    """Should reject non-WAV uploads with 400."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/predict/wav",
            files={"file": ("test.mp3", b"fake", "audio/mpeg")},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_predict_spectrogram_wrong_extension():
    """Should reject non-PNG uploads with 400."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/predict/spectrogram",
            files={"file": ("test.jpg", b"fake", "image/jpeg")},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_predict_spectrogram_invalid_png():
    """Should return 503 (no model) or 422 (bad image) — not 500."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/predict/spectrogram",
            files={"file": ("test.png", b"not-a-png", "image/png")},
        )
    assert response.status_code in (422, 503)
