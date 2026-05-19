# NeuroSound — AI-Powered Acoustic Classification

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange.svg)](https://tensorflow.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Upload any WAV audio file or PNG spectrogram — NeuroSound classifies the sound in milliseconds using two state-of-the-art deep learning models trained on ESC-50.

---

## Models

| Model | Input | Accuracy | Architecture |
|-------|-------|----------|--------------|
| **EfficientNetB3 + Attention** | PNG spectrogram | **93.34%** | EfficientNetB3 + Multi-Head Attention |
| **YAMNet** | WAV audio | **88.5%** | MobileNet-based, pretrained on AudioSet 2M clips |

Both models classify **50 environmental sound categories** from the ESC-50 dataset — exceeding the human baseline of 81%.

---

## Features

- **Dual-model inference** — WAV files → YAMNet, PNG spectrograms → EfficientNetB3
- **Top-5 predictions** with confidence scores
- **Prediction history** stored in SQLite, browsable and deletable
- **Single-page frontend** (vanilla JS SPA, no build step)
- **Production-ready backend** — async FastAPI, model registry loaded once at startup, Dockerized

---

## Project Structure

```
NeuroSound/
├── Backend/                    # FastAPI API server
│   ├── main.py                 # App entry point + model lifespan
│   ├── routers/
│   │   ├── predict.py          # POST /api/predict/wav  +  /spectrogram
│   │   ├── history.py          # GET/DELETE /api/history
│   │   └── health.py           # GET /api/health
│   ├── services/
│   │   ├── yamnet_service.py   # WAV → YAMNet embedding → prediction
│   │   └── spectrogram_service.py  # PNG → EfficientNetB3 → prediction
│   ├── database/               # Async SQLAlchemy + SQLite
│   ├── schemas/                # Pydantic v2 request/response models
│   ├── Models/
│   │   ├── yamnet_esc50.keras      # YAMNet classification head (7.8 MB)
│   │   └── spectrogram_model.keras # EfficientNetB3 (105 MB — see below)
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── Frontend/                   # Vanilla JS SPA
│   └── index.html              # Full app — Landing + Dashboard + History + About
│
├── generate_spectrograms.py    # Mel spectrogram generation from ESC-50 WAV files
├── train_spectrogram.ipynb     # EfficientNetB3 training notebook
├── yamnet_esc50.ipynb          # YAMNet fine-tuning notebook
└── requirements.txt            # Training dependencies
```

---

## Getting Started

### Backend

```bash
cd Backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/api/docs`

> **Note on `spectrogram_model.keras`** — this file is 105 MB and excluded from the repository.  
> Download it from the [Releases](../../releases) page and place it at `Backend/Models/spectrogram_model.keras`.

### Frontend

```bash
cd Frontend
node serve.mjs   # serves on http://localhost:3000
```

### Docker (Backend)

```bash
cd Backend
docker build -t neurosound-api .
docker run -p 8000:8000 neurosound-api
```

---

## API Reference

### `POST /api/predict/wav`
Upload a `.wav` file for YAMNet classification.

```bash
curl -X POST http://localhost:8000/api/predict/wav \
  -F "file=@audio.wav"
```

### `POST /api/predict/spectrogram`
Upload a `.png` spectrogram for EfficientNetB3 classification.

```bash
curl -X POST http://localhost:8000/api/predict/spectrogram \
  -F "file=@spectrogram.png"
```

### `GET /api/history`
Retrieve prediction history (most recent first).

### `GET /api/health`
Returns model load status.

**Response schema:**
```json
{
  "prediction": "dog",
  "confidence": 0.9412,
  "top5": [
    {"label": "dog", "confidence": 0.9412},
    {"label": "cat", "confidence": 0.0321},
    ...
  ],
  "model": "yamnet",
  "filename": "audio.wav",
  "input_type": "wav",
  "timestamp": "2025-05-18T14:32:00Z"
}
```

---

## ESC-50 Sound Categories

50 classes across 5 groups:

| Group | Classes |
|-------|---------|
| Animals | dog, cat, cow, sheep, hen, pig, frog, rooster, crow, insects |
| Nature | rain, wind, sea_waves, thunderstorm, crickets, crackling_fire, chirping_birds, pouring_water, toilet_flush, water_drops |
| Human | laughing, crying_baby, coughing, sneezing, clapping, footsteps, snoring, breathing, brushing_teeth, drinking_sipping |
| Interior | keyboard_typing, mouse_click, clock_tick, clock_alarm, washing_machine, vacuum_cleaner, glass_breaking, door_wood_knock, door_wood_creaks, can_opening |
| Urban | airplane, helicopter, train, engine, car_horn, siren, chainsaw, hand_saw, church_bells, fireworks |

---

## Training

The EfficientNetB3 model was trained in two phases:
- **Phase 1** — backbone frozen, lr=8e-4, classification head trained from scratch
- **Phase 2** — fine-tuning with 20 top layers unfrozen, batch normalization frozen

YAMNet uses transfer learning from Google's AudioSet-pretrained hub model, with a dense residual classification head trained on ESC-50 with 5× data augmentation and label smoothing.

Training notebooks: `train_spectrogram.ipynb`, `yamnet_esc50.ipynb`

---

## Stack

- **Backend** — FastAPI, TensorFlow 2.15, YAMNet (TF Hub), librosa, SQLAlchemy async, Pydantic v2
- **Frontend** — Vanilla JS SPA, Tailwind CSS CDN, Syne + DM Mono + Outfit fonts
- **Infrastructure** — Uvicorn, Docker, SQLite + aiosqlite

---

## License

MIT — see [LICENSE](LICENSE)
