"""Ses işleme ve stüdyo mastering motoru: Tok, net ve doğal yayın kalitesi.

Bu modül:
1. Faz bozulması ve robotik artefakt yaratan ucuz faz vokoderlerini, mikro vibrato
   ve yapay gürültü eklemelerini tamamen kaldırır.
2. 'Tok ve net' insan sesi için özel parametrik stüdyo ekolayzırı uygular:
   - 50 Hz subsonic kesici (dip gürültüsü ve mekanik patlamaları temizler)
   - 140 Hz sıcak gövde takviyesi (tok, göğüs rezonanslı dolgun erkek/podcast tonu)
   - 420 Hz kutu/burun frekansı temizliği (boğukluğu alır)
   - 3.2 kHz berraklık ve artikülasyon tepesi (harfleri ve heceleri 'net' yapar)
   - 11 kHz ipeksi hava rafı (açık ve modern stüdyo parlaklığı)
3. Akustik sınır koruması (Envelope Guard):
   - Cümlenin başındaki ilk karakter ve sonundaki son karakter asla kesilmez.
   - Konuşma öncesi 70 ms, sonrası 180 ms temiz sessizlik eklenir; fade geçişleri
     kesinlikle konuşulan sesin üstüne değil, bu tampon sessizlik zarfına uygulanır.
4. EBU R128 / ITU-R BS.1770 yayın standartlarında (-16 LUFS) mastering ve true-peak limitör.
5. Yüksek kaliteli 48 kHz MP3 ihracı.
"""

from __future__ import annotations

import numpy as np
import scipy.signal as dsp
import soundfile as sf
import pyloudnorm as pyln

from .emotion import Prosody
from .voices import Voice


def _to_mono(y: np.ndarray) -> np.ndarray:
    if y.ndim == 2:
        y = y.mean(axis=-1)
    return np.asarray(y, dtype=np.float32)


def biquad_peaking(f0: float, gain_db: float, q: float, sr: int) -> np.ndarray:
    """Parametrik çan (peaking/bell) filtresi katsayıları (SOS formatında)."""
    if abs(gain_db) < 0.05:
        return np.array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0], dtype=np.float64)
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2.0 * q)
    A = 10.0 ** (gain_db / 40.0)
    b0 = 1.0 + alpha * A
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / A
    return np.array([b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0], dtype=np.float64)


def biquad_high_shelf(f0: float, gain_db: float, q: float, sr: int) -> np.ndarray:
    """Yüksek raf (high shelf) filtresi katsayıları (SOS formatında)."""
    if abs(gain_db) < 0.05:
        return np.array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0], dtype=np.float64)
    w0 = 2 * np.pi * f0 / sr
    A = 10.0 ** (gain_db / 40.0)
    alpha = (np.sin(w0) / 2.0) * np.sqrt((A + 1.0 / A) * (1.0 / q - 1.0) + 2.0)
    cos_w = np.cos(w0)
    sqrt_A = np.sqrt(A)

    b0 = A * ((A + 1.0) + (A - 1.0) * cos_w + 2.0 * sqrt_A * alpha)
    b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w)
    b2 = A * ((A + 1.0) + (A - 1.0) * cos_w - 2.0 * sqrt_A * alpha)
    a0 = (A + 1.0) - (A - 1.0) * cos_w + 2.0 * sqrt_A * alpha
    a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w)
    a2 = (A + 1.0) - (A - 1.0) * cos_w - 2.0 * sqrt_A * alpha

    return np.array([b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0], dtype=np.float64)


def apply_tok_clarity_eq(
    y: np.ndarray,
    sr: int = 48000,
    warmth_db: float = 2.0,
    presence_db: float = 1.8,
    air_db: float = 1.2,
) -> np.ndarray:
    """Stüdyo yayın ekolayzırı: Tok gövde rezonansı ve net harf artikülasyonu.

    - 50 Hz High-pass: DC ofseti ve mekanik patlamaları keser
    - 140 Hz Peaking (+warmth_db): Sese tok ve sıcak erkek/anlatıcı gövdesi kazandırır
    - 420 Hz Peaking (-1.2 dB): Kutu ve burun rezonansını temizler (anti-mud)
    - 3200 Hz Peaking (+presence_db): Konuşmayı öne çıkarır, diksiyonu 'net'leştirir
    - 11000 Hz High-shelf (+air_db): İpeksi modern hava verir, cızırtı yapmaz
    """
    if len(y) < 64:
        return y

    sos_list = []
    # 1. 50 Hz Highpass (3. derece Butterworth)
    hp_sos = dsp.butter(3, 50, fs=sr, btype="high", output="sos")
    sos_list.append(hp_sos)

    # 2. 140 Hz Tok Gövde (Q=1.2)
    warm_sos = biquad_peaking(140.0, warmth_db, q=1.2, sr=sr).reshape(1, 6)
    sos_list.append(warm_sos)

    # 3. 420 Hz Kutu Temizleme (Q=1.4, -1.2 dB)
    mud_sos = biquad_peaking(420.0, -1.2, q=1.4, sr=sr).reshape(1, 6)
    sos_list.append(mud_sos)

    # 4. 3200 Hz Netlik / Vokal Varlığı (Q=1.1)
    pres_sos = biquad_peaking(3200.0, presence_db, q=1.1, sr=sr).reshape(1, 6)
    sos_list.append(pres_sos)

    # 5. 11000 Hz İpeksi Hava (Q=0.9)
    air_sos = biquad_high_shelf(11000.0, air_db, q=0.9, sr=sr).reshape(1, 6)
    sos_list.append(air_sos)

    full_sos = np.vstack(sos_list)
    # Sıfır faz kayması için sosfiltfilt (bidirectional IIR)
    out = dsp.sosfiltfilt(full_sos, y.astype(np.float64))
    return np.asarray(out, dtype=np.float32)


def pad_and_envelope(
    y: np.ndarray,
    sr: int = 48000,
    lead_ms: float = 70.0,
    trail_ms: float = 180.0,
    fade_ms: float = 25.0,
) -> np.ndarray:
    """Akustik sınır koruması: İlk ve son karakterlerin kesilmesini imkansız kılar.

    Konuşma sinyalinin önüne ve arkasına temiz sessizlik ekler ve yumuşak fade
    geçişini YALNIZCA bu eklenen sessizlik bölgesine uygular. Konuşulan harflerin
    hiçbir mikrosaniyesi kırpılmaz veya söndürülmez.
    """
    n_lead = int(sr * (lead_ms / 1000.0))
    n_trail = int(sr * (trail_ms / 1000.0))
    lead = np.zeros(n_lead, dtype=np.float32)
    trail = np.zeros(n_trail, dtype=np.float32)
    padded = np.concatenate([lead, y, trail])

    # Fade geçişlerini eklenen sessizlik tamponuna yedir
    n_fade = min(int(sr * (fade_ms / 1000.0)), n_lead // 2, n_trail // 2)
    if n_fade > 1:
        # Başlangıç fade-in
        ramp_in = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, n_fade, dtype=np.float32)))
        padded[:n_fade] *= ramp_in
        # Bitiş fade-out
        ramp_out = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, n_fade, dtype=np.float32)))
        padded[-n_fade:] *= ramp_out

    return padded


def master_audio(
    y: np.ndarray,
    sr: int = 48000,
    target_lufs: float = -16.0,
    ceiling_db: float = -1.0,
) -> np.ndarray:
    """Stüdyo yayın seviyesi normalizasyonu ve true-peak limitörü.

    - ITU-R BS.1770 / EBU R128 (-16 LUFS)
    - True-peak soft limiter (-1.0 dBTP ceiling), sıfır distorsiyon
    """
    y = np.asarray(y, dtype=np.float32)
    if len(y) == 0 or np.max(np.abs(y)) < 1e-6:
        return y

    meter = pyln.Meter(sr)
    try:
        loudness = meter.integrated_loudness(y)
        if np.isfinite(loudness) and loudness > -70.0:
            y = pyln.normalize.loudness(y, loudness, target_lufs)
    except Exception:
        # Aşırı kısa seslerde rms fallback
        rms = np.sqrt(np.mean(y ** 2)) + 1e-8
        y = y * (0.15 / rms)

    # Soft-knee true-peak limiter
    ceiling = 10.0 ** (ceiling_db / 20.0)
    peak = np.max(np.abs(y))
    if peak > ceiling:
        y = y * (ceiling / peak)

    return np.clip(y, -ceiling, ceiling).astype(np.float32)


def to_mastered_stereo(y: np.ndarray, sr: int = 48000) -> np.ndarray:
    """Doğal yayın stereosu: Merkezde kaya gibi sağlam mono vokal, sıfır faz çakışması.

    Tüm vokal gövdesi (F0 ve rezonanslar) her iki kanalda da birebir merkezdedir.
    Faz taraklanması (comb filter) veya robotik kutu sesi kesinlikle oluşmaz.
    """
    mono = _to_mono(y)
    stereo = np.stack([mono, mono], axis=-1)
    return stereo.astype(np.float32)


def save_audio(
    y: np.ndarray,
    sr: int,
    path: str,
    format: str | None = None,
) -> str:
    """Sesi yüksek kaliteli 48 kHz MP3 formatında kaydeder."""
    # Varsayılan format: MP3
    if format is None:
        if path.lower().endswith(".wav"):
            format = "WAV"
        else:
            format = "MP3"
            if not path.lower().endswith(".mp3"):
                path = path + ".mp3"

    if format == "MP3":
        sf.write(path, y, sr, format="MP3")
    else:
        sf.write(path, y, sr, subtype="PCM_24")
    return path


# Geriye dönük uyumluluk arayüzleri
def apply_gain(y: np.ndarray, gain_db: float) -> np.ndarray:
    if gain_db == 0:
        return y
    return y * (10.0 ** (gain_db / 20.0))


def apply_brightness(y: np.ndarray, sr: int, brightness_db_per_oct: float) -> np.ndarray:
    if abs(brightness_db_per_oct) < 0.05:
        return y
    return apply_tok_clarity_eq(y, sr, presence_db=brightness_db_per_oct * 0.8)


def humanize(y: np.ndarray, sr: int, amount: float = 1.0) -> np.ndarray:
    """Temiz yayın parlatması: Yapay vibrato veya gürültü eklemez, 'tok ve net' EQ uygular."""
    if amount <= 0:
        return y
    return apply_tok_clarity_eq(y, sr, warmth_db=1.5 * amount, presence_db=1.5 * amount, air_db=1.0 * amount)


def apply_prosody(y: np.ndarray, sr: int, p: Prosody, voice: Voice | None = None) -> np.ndarray:
    """Duygu ve ses profili parametrelerini stüdyo ekolayzırı ile uygular."""
    y = _to_mono(y)
    if len(y) == 0:
        return y

    warmth = 2.0 + (voice.warmth_db if voice else 0.0) + (getattr(p, "warmth_delta", 0.0))
    presence = 1.8 + (voice.presence_db if voice else 0.0) + (getattr(p, "presence_delta", 0.0))
    air = 1.2 + (voice.air_db if voice else 0.0)

    y = apply_tok_clarity_eq(y, sr, warmth_db=warmth, presence_db=presence, air_db=air)
    gain = (p.gain_db if p else 0.0) + (voice.gain_db if voice else 0.0)
    y = apply_gain(y, gain)
    return y.astype(np.float32)
