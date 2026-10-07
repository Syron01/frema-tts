"""Ses işleme: prozodi uygulama + insanileştirme (AI likini kırma)."""

from __future__ import annotations

import numpy as np
import librosa
import scipy.signal as dsp

from .emotion import Prosody
from .voices import Voice


def _to_mono(y: np.ndarray) -> np.ndarray:
    if y.ndim == 2:
        y = y.mean(axis=0)
    return np.asarray(y, dtype=np.float32)


def apply_gain(y: np.ndarray, gain_db: float) -> np.ndarray:
    if gain_db == 0:
        return y
    return y * (10 ** (gain_db / 20.0))


def apply_brightness(y: np.ndarray, sr: int, brightness_db_per_oct: float) -> np.ndarray:
    if brightness_db_per_oct == 0:
        return y
    # 1 oktav üstüne her +dB
    n = len(y)
    freqs = np.fft.rfftfreq(n, 1 / sr)
    mag = np.fft.rfft(y)
    ref = max(freqs[1], 1.0)
    tilt = brightness_db_per_oct * np.log2(np.maximum(freqs, ref) / ref) / 12.0
    tilt = np.clip(tilt, -18, 18)
    mag = mag * (10 ** (tilt / 20.0))
    out = np.fft.irfft(mag, n).astype(np.float32)
    return out


def apply_lowpass(y: np.ndarray, sr: int, cutoff: float | None) -> np.ndarray:
    if cutoff is None or cutoff >= sr / 2:
        return y
    sos = dsp.butter(6, cutoff, fs=sr, btype="low", output="sos")
    return dsp.sosfiltfilt(sos, y).astype(np.float32)


def pitch_shift(y: np.ndarray, sr: int, semitones: float) -> np.ndarray:
    if semitones == 0:
        return y
    return librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitones).astype(np.float32)


def change_rate(y: np.ndarray, rate: float) -> np.ndarray:
    """Zaman uzatma/sıkıştırma (pitch sabit kalır çünkü sonra pitch uygulanır).
    Pratikte: resample + pitch geri alma yerine basit time-stretchld."""
    if rate == 1.0:
        return y
    return librosa.effects.time_stretch(y, rate=rate).astype(np.float32)


def _vibrato(y: np.ndarray, sr: int, cents: float, hz: float) -> np.ndarray:
    if cents <= 0 or hz <= 0:
        return y
    t = np.arange(len(y)) / sr
    depth = 2 ** (cents / 1200.0) - 1.0
    mod = 1.0 + depth * np.sin(2 * np.pi * hz * t)
    # değişken hızlı resampling
    idx = np.cumsum(mod) / mod.mean()
    idx = idx / idx[-1] * (len(y) - 1)
    out = np.interp(np.arange(len(y)), idx, y).astype(np.float32)
    return out


def _tremolo(y: np.ndarray, sr: int, db: float, hz: float) -> np.ndarray:
    if db <= 0 or hz <= 0:
        return y
    t = np.arange(len(y)) / sr
    mod = 1.0 + (10 ** (db / 20) - 1.0) * 0.5 * (1 + np.sin(2 * np.pi * hz * t))
    return y * mod.astype(np.float32)


def add_breathiness(y: np.ndarray, sr: int, amount: float) -> np.ndarray:
    if amount <= 0:
        return y
    noise = np.random.default_rng(0).standard_normal(len(y)).astype(np.float32) * 0.02
    noise = dsp.sosfiltfilt(dsp.butter(2, 6000, fs=sr, btype="high", output="sos"), noise)
    return (y * (1 - amount * 0.4) + noise * amount).astype(np.float32)


def humanize(y: np.ndarray, sr: int, amount: float = 1.0) -> np.ndarray:
    """AI likini kıran küçük sapmalar: mikro pitch titreşimi, çok düşük oda tonu,
    hafif dithering."""
    if amount <= 0:
        return y
    rng = np.random.default_rng(42)
    # mikro vibrato (merdiven yerine yumuşak)
    cents = 6.0 * amount
    y = _vibrato(y, sr, cents, 5.0)
    # çok hafif analojik sıcaklık: 8kHz üstü tavana yumuşatma
    y = apply_lowpass(y, sr, min(sr / 2, 9500))
    # dither
    y = y + rng.standard_normal(len(y)).astype(np.float32) * (1e-4 * amount)
    # normalize
    peak = np.max(np.abs(y)) + 1e-8
    y = y / max(peak, 1.0)
    return y.astype(np.float32)


def apply_prosody(y: np.ndarray, sr: int, p: Prosody, voice: Voice | None = None) -> np.ndarray:
    y = _to_mono(y)
    if len(y) == 0 or np.sqrt(np.mean(y ** 2)) < 1e-5:
        return y
    rate = p.rate * (voice.rate if voice else 1.0)
    y = change_rate(y, rate)
    semis = p.pitch_semitones + (voice.pitch_semitones if voice else 0.0)
    y = pitch_shift(y, sr, semis)
    y = _vibrato(y, sr, p.vibrato_cents, p.vibrato_hz)
    y = _tremolo(y, sr, p.tremolo_db, p.tremolo_hz)
    y = apply_brightness(y, sr, p.brightness + (voice.brightness if voice else 0.0))
    y = apply_lowpass(y, sr, voice.lowpass_hz if voice else None)
    breath = max(p.breathiness, voice.breathiness if voice else 0.0)
    y = add_breathiness(y, sr, breath)
    y = apply_gain(y, p.gain_db + (voice.gain_db if voice else 0.0))
    y = humanize(y, sr, amount=0.7)
    peak = np.max(np.abs(y)) + 1e-8
    if peak > 1.0:
        y = y / peak
    return y.astype(np.float32)
