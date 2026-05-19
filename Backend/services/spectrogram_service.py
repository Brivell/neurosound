import logging

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input

from config import get_settings

settings = get_settings()
logger   = logging.getLogger(__name__)

ESC50_LABELS = [
    "dog", "sheep", "hen", "cow", "insects", "frog", "pig", "rooster",
    "cat", "crow", "chirping_birds", "rain", "wind", "sea_waves",
    "crickets", "thunderstorm", "pouring_water", "toilet_flush",
    "crackling_fire", "water_drops", "brushing_teeth", "laughing",
    "crying_baby", "clapping", "footsteps", "drinking_sipping",
    "snoring", "coughing", "sneezing", "breathing", "vacuum_cleaner",
    "mouse_click", "washing_machine", "clock_tick", "glass_breaking",
    "door_wood_creaks", "keyboard_typing", "clock_alarm", "can_opening",
    "door_wood_knock", "chainsaw", "airplane", "train", "engine",
    "siren", "hand_saw", "helicopter", "car_horn", "church_bells",
    "fireworks",
]


def preprocess_png(file_bytes: bytes) -> np.ndarray:
    """Decode PNG bytes → EfficientNetB3 input array (1, 300, 300, 3)."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image — invalid PNG file")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (settings.image_size, settings.image_size))
    img = preprocess_input(img.astype(np.float32))
    return np.expand_dims(img, axis=0)


def predict(file_bytes: bytes, model) -> dict:
    """Full EfficientNetB3 inference pipeline."""
    img_array = preprocess_png(file_bytes)
    probs     = model.predict(img_array, verbose=0)[0]
    top5_idx  = np.argsort(probs)[::-1][:5]
    pred_idx  = int(np.argmax(probs))

    return {
        "prediction": ESC50_LABELS[pred_idx],
        "confidence": float(probs[pred_idx]),
        "top5": [
            {"label": ESC50_LABELS[i], "confidence": float(probs[i])}
            for i in top5_idx
        ],
        "model": "efficientnetb3",
    }
