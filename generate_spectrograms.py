# =============================================================================
# GÉNÉRATION DE SPECTROGRAMMES MEL AUGMENTÉS — ESC-50
# =============================================================================
# Ce script lit les fichiers WAV du dossier new-esc50,
# génère 7 variantes audio par fichier, et sauvegarde chaque variante
# en spectrogramme Mel PNG 224×224.
#
# Résultat : ~14 000 images au lieu de 2 000
#            → ~280 images par classe au lieu de 40
#
# Usage :
#   pip install librosa
#   python generate_spectrograms.py
# =============================================================================

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # pas de fenêtre graphique — plus rapide
import matplotlib.pyplot as plt
import librosa
import librosa.display
from tqdm import tqdm

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

# Dossier contenant les WAV ET les PNG originaux
WAV_DIR  = r"C:\Users\amaur\Documents\Portfolio\Portfolio\PI3\new-esc50"

# Dossier de sortie pour les nouveaux spectrogrammes augmentés
# (dossier séparé pour ne pas mélanger avec les originaux)
OUT_DIR  = r"C:\Users\amaur\Documents\Portfolio\Portfolio\PI3\new-esc50-augmented"

# CSV original
CSV_PATH = r"C:\Users\amaur\Documents\Portfolio\Portfolio\PI3\new_esc50.csv"

# CSV de sortie (nouveau dataset augmenté)
OUT_CSV  = r"C:\Users\amaur\Documents\Portfolio\Portfolio\PI3\esc50_augmented.csv"

os.makedirs(OUT_DIR, exist_ok=True)

# ── Paramètres Mel optimisés pour ESC-50 ──────────────────────────────────────
SR     = 22050   # fréquence d'échantillonnage
N_MELS = 128     # résolution fréquentielle
N_FFT  = 2048    # taille de la fenêtre FFT
HOP    = 512     # pas entre chaque fenêtre
FMAX   = 8000    # fréquence max utile pour les sons environnementaux


# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def wav_to_mel_db(y, sr=SR):
    """Convertit un signal audio en spectrogramme Mel en décibels."""
    mel = librosa.feature.melspectrogram(
        y=y, sr=sr,
        n_mels=N_MELS,
        n_fft=N_FFT,
        hop_length=HOP,
        fmax=FMAX,
    )
    # Conversion en dB : fait ressortir les détails dans les sons faibles
    return librosa.power_to_db(mel, ref=np.max)


def save_spectrogram(mel_db, out_path):
    """
    Sauvegarde le spectrogramme en PNG 224×224.
    Pas d'axes ni de marges — image pure pour le CNN.
    """
    fig, ax = plt.subplots(figsize=(2.24, 2.24), dpi=100)
    ax.axis("off")
    librosa.display.specshow(
        mel_db, sr=SR, hop_length=HOP,
        fmax=FMAX, cmap="viridis", ax=ax
    )
    plt.tight_layout(pad=0)
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def get_augmentations(y, sr=SR):
    """
    Génère 7 variantes audio du signal original.
    Chaque variante produit un spectrogramme visuellement distinct.

    ┌─────────────────┬──────────────────────────────────────────────┐
    │ Variante        │ Description                                  │
    ├─────────────────┼──────────────────────────────────────────────┤
    │ original        │ Signal brut sans modification                │
    │ noise           │ Bruit blanc léger (simule environnement réel)│
    │ shift_fwd       │ Décalage temporel +0.5s                      │
    │ shift_bwd       │ Décalage temporel -0.5s                      │
    │ pitch_up        │ Hausse de 2 demi-tons                        │
    │ pitch_down      │ Baisse de 2 demi-tons                        │
    │ speed_up        │ Accélération +10% (sans changer le pitch)    │
    └─────────────────┴──────────────────────────────────────────────┘
    """
    augmented = {
        "original":   y,
        "noise":      y + 0.005 * np.random.randn(len(y)),
        "shift_fwd":  np.roll(y,  int(sr * 0.5)),
        "shift_bwd":  np.roll(y, -int(sr * 0.5)),
        "pitch_up":   librosa.effects.pitch_shift(y, sr=sr, n_steps=2),
        "pitch_down": librosa.effects.pitch_shift(y, sr=sr, n_steps=-2),
        "speed_up":   librosa.effects.time_stretch(y, rate=1.1),
        "speed_down":  librosa.effects.time_stretch(y, rate=0.9),
        "pitch_up2":   librosa.effects.pitch_shift(y, sr=sr, n_steps=4),
        "noise_heavy": np.clip(y + 0.01 * np.random.randn(len(y)).astype(np.float32), -1, 1).astype(np.float32),
    }
    return augmented


# ─────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────

if __name__ == "__main__":
    df = pd.read_csv(CSV_PATH, sep=";",
                     dtype={"filename": str, "category": str, "target": int})

    print(f"📂 Dataset original : {len(df)} fichiers WAV")
    print(f"   Dossier source   : {WAV_DIR}")
    print(f"   Dossier sortie   : {OUT_DIR}")
    print(f"   Variantes/fichier: 7")
    print(f"   Total attendu    : ~{len(df) * 7} spectrogrammes\n")

    records  = []
    errors   = 0
    skipped  = 0

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Génération"):

        # Le CSV contient "1-137-A-32.wav" — le WAV est dans WAV_DIR
        wav_path = os.path.join(WAV_DIR, row["filename"])

        if not os.path.exists(wav_path):
            errors += 1
            continue

        # Chargement audio (5 secondes, rééchantillonné à SR)
        try:
            y, sr = librosa.load(wav_path, sr=SR, duration=5.0)
        except Exception as e:
            print(f"  ⚠️  Erreur chargement {row['filename']} : {e}")
            errors += 1
            continue

        # Extraction du numéro de fold depuis le nom de fichier
        # Convention ESC-50 : "1-137-A-32.wav" → fold 1
        fold = int(row["filename"].split("-")[0])

        # Génération des 7 variantes
        for aug_name, y_aug in get_augmentations(y, sr).items():

            # Nom du PNG de sortie : "1-137-A-32_original.png"
            out_name = f"{os.path.splitext(row['filename'])[0]}_{aug_name}.png"
            out_path = os.path.join(OUT_DIR, out_name)

            # Ne régénère pas si déjà existant (reprise possible si interruption)
            if os.path.exists(out_path):
                skipped += 1
            else:
                try:
                    mel_db = wav_to_mel_db(y_aug, sr)
                    save_spectrogram(mel_db, out_path)
                except Exception as e:
                    print(f"  ⚠️  Erreur génération {out_name} : {e}")
                    errors += 1
                    continue

            records.append({
                "filename": out_name,
                "category": row["category"],
                "target":   row["target"],
                "fold":     fold,
                "aug":      aug_name,
            })

    # ── Sauvegarde du nouveau CSV ──────────────────────────────────────────────
    df_aug = pd.DataFrame(records)
    df_aug.to_csv(OUT_CSV, index=False, sep=";")

    # ── Résumé ────────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"✅ GÉNÉRATION TERMINÉE")
    print(f"{'='*55}")
    print(f"   Spectrogrammes générés  : {len(df_aug)}")
    print(f"   Images par classe (moy) : {len(df_aug) // 50}")
    print(f"   Déjà existants (skip)   : {skipped}")
    print(f"   Erreurs                 : {errors}")
    print(f"   Nouveau CSV             → {OUT_CSV}")
    print(f"\n📌 Pour utiliser ce dataset dans train_spectrogram.py :")
    print(f"   CSV_PATH = r\"{OUT_CSV}\"")
    print(f"   IMG_DIR  = r\"{OUT_DIR}\"")
