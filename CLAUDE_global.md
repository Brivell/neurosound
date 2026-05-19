# CLAUDE.md — NeuroSound Platform (Global)

## Project Overview
NeuroSound is a professional web platform for acoustic sound classification
using two deep learning models trained on ESC-50 (50 environmental sound classes).

**Tagline:** AI-powered acoustic intelligence
**Audience:** Engineers, researchers, data scientists
**Stack:** FastAPI (backend) + HTML/CSS/JS (frontend) + SQLite (database)

---

## Project Structure
```
neurosound/
├── CLAUDE.md                  ← this file (global rules)
├── frontend/
│   ├── CLAUDE.md              ← frontend rules
│   ├── index.html             ← single page application
│   ├── brand_assets/
│   │   ├── logo.svg
│   │   └── colors.md
│   ├── serve.mjs              ← local dev server
│   └── screenshot.mjs         ← puppeteer screenshot tool
├── backend/
│   ├── CLAUDE.md              ← backend rules
│   ├── main.py                ← FastAPI app entry point
│   ├── routers/
│   │   ├── predict.py         ← prediction endpoints
│   │   └── history.py         ← history endpoints
│   ├── services/
│   │   ├── yamnet_service.py  ← YAMNet inference
│   │   └── spectrogram_service.py ← EfficientNetB3 inference
│   ├── models/
│   │   ├── spectrogram_model.keras  ← EfficientNetB3 (93.34%)
│   │   └── yamnet_esc50.keras       ← YAMNet (88.5%)
│   ├── database/
│   │   └── db.py              ← SQLite + SQLAlchemy
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Models
```
Model 1 : EfficientNetB3 + Multi-Head Attention
  Input   : PNG spectrogram (300×300)
  Output  : 50 ESC-50 classes
  Accuracy: 93.34% test accuracy

Model 2 : YAMNet (Google AudioSet)
  Input   : WAV file (16kHz mono)
  Output  : 50 ESC-50 classes
  Accuracy: 88.5% val accuracy

Dataset : ESC-50
  Classes : 50 environmental sound categories
  Labels  : dog, rain, chainsaw, siren, crying_baby, etc.
```

---

## ESC-50 Classes (target 0→49)
```
dog, sheep, hen, cow, insects, frog, pig, rooster, cat, crow,
chirping_birds, rain, wind, sea_waves, crickets, thunderstorm,
pouring_water, toilet_flush, crackling_fire, water_drops,
brushing_teeth, laughing, crying_baby, clapping, footsteps,
drinking_sipping, snoring, coughing, sneezing, breathing,
vacuum_cleaner, mouse_click, washing_machine, clock_tick,
glass_breaking, door_wood_creaks, keyboard_typing, clock_alarm,
can_opening, door_wood_knock, chainsaw, airplane, train, engine,
siren, hand_saw, helicopter, car_horn, church_bells, fireworks
```

---

## Brand Identity

### Colors
```
--bg-primary    : #0A0E1A
--bg-secondary  : #111827
--bg-elevated   : #1C2333
--accent-cyan   : #00D4FF
--accent-violet : #7C3AED
--success       : #10B981
--warning       : #F59E0B
--error         : #EF4444
--text-primary  : #F9FAFB
--text-muted    : #6B7280
--border        : rgba(0, 212, 255, 0.12)
```

### Typography
```
Display : "Syne"    → headings, hero text
Body    : "DM Mono" → labels, data, predictions, code
UI      : "Outfit"  → buttons, nav, paragraphs
```

---

## API Contract
```
POST /api/predict/wav
  Body    : multipart/form-data { file: .wav }
  Returns : { prediction, confidence, top5, model, timestamp }

POST /api/predict/spectrogram
  Body    : multipart/form-data { file: .png }
  Returns : { prediction, confidence, top5, model, timestamp }

GET  /api/history
  Returns : [ { id, timestamp, input_type, filename, prediction, confidence } ]

DELETE /api/history/{id}
  Returns : { success: true }

GET  /api/health
  Returns : { status: "ok", models_loaded: true }
```

---

## Database Schema
```sql
CREATE TABLE predictions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    input_type  TEXT NOT NULL,   -- 'wav' or 'spectrogram'
    filename    TEXT NOT NULL,
    model_used  TEXT NOT NULL,   -- 'yamnet' or 'efficientnetb3'
    prediction  TEXT NOT NULL,
    confidence  REAL NOT NULL,
    top5        TEXT NOT NULL    -- JSON string
);
```

---

## Global Rules
- Never hardcode model paths — use environment variables or config file
- Always validate file types before sending to model (WAV or PNG only)
- CORS must allow frontend origin in development (`http://localhost:3000`)
- All API responses must follow the contract above exactly
- Never expose raw TensorFlow errors to the frontend — catch and return clean messages
- Models must be loaded once at startup — never reload per request
