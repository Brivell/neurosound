import io
import logging

import librosa
import numpy as np
import soundfile as sf
import tensorflow as tf

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


def preprocess_wav(file_bytes: bytes) -> tf.Tensor:
    """Load WAV bytes → mono 16 kHz float32 tensor, fixed duration."""
    target_sr  = settings.sample_rate
    target_len = target_sr * settings.audio_duration

    try:
        y, sr = sf.read(io.BytesIO(file_bytes))
    except Exception:
        y, sr = librosa.load(
            io.BytesIO(file_bytes),
            sr=target_sr, mono=True,
            duration=settings.audio_duration,
        )
        return tf.constant(y, dtype=tf.float32)

    if y.ndim > 1:
        y = y.mean(axis=1)

    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]

    return tf.constant(y.astype(np.float32), dtype=tf.float32)


def predict(file_bytes: bytes, yamnet_hub, model) -> dict:
    """Full YAMNet inference pipeline."""
    wav_tensor = preprocess_wav(file_bytes)

    _, embeddings, _ = yamnet_hub(wav_tensor)
    emb = tf.reduce_mean(embeddings, axis=0).numpy()
    emb = np.expand_dims(emb, axis=0)

    probs    = model.predict(emb, verbose=0)[0]
    top5_idx = np.argsort(probs)[::-1][:5]
    pred_idx = int(np.argmax(probs))

    return {
        "prediction": ESC50_LABELS[pred_idx],
        "confidence": float(probs[pred_idx]),
        "top5": [
            {"label": ESC50_LABELS[i], "confidence": float(probs[i])}
            for i in top5_idx
        ],
        "model": "yamnet",
    }
