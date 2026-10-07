"""Ses işleme: prozodi uygulama + insanileştirme (AI likini kırma).

Kasıtlı tasarım kararları:
- Pitch kaydırma PSOLA (parselmouth/Praat) ile yapılır; librosa faz vokoderi
  yerine çok daha az 'robot' yapar. Yoksa librosa'ya düşer.
- Duygu hızı (rate) 'kaset' usulü resample ile değişir; F0 da doğal süre
  uzadıkça alçalır/yükselir, faz vokoderi hiç kullanılmaz.
- Konuşma kanalı (formant) dönüşümü resample + süre geri kazanımı ile yapılır;
  erkek sesi yalnızca per değil, ses yolu daraltılarak elde edilir.
"""

from __future__ import annotations

import numpy as np
import librosa
import scipy.signal as dsp

from .emotion import Prosody
from .voices import Voice

try:
    import parselmouth
    from parselmouth.praat import call as _praat
    _HAVE_PRAAT = True
except Exception:  # pragma: no cover
    _HAVE_PRAAT = False


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
    n = len(y)
    freqs = np.fft.rfftfreq(n, 1 / sr)
    mag = np.fft.rfft(y)
    ref = max(freqs[1], 1.0)
    tilt = brightness_db_per_oct * np.log2(np.maximum(freqs, ref) / ref) / 12.0
    tilt = np.clip(tilt, -18, 18)
    mag = mag * (10 ** (tilt / 20.0))
    return np.fft.irfft(mag, n).astype(np.float32)


def apply_lowpass(y: np.ndarray, sr: int, cutoff: float | None) -> np.ndarray:
    if cutoff is None or cutoff >= sr / 2:
        return y
    sos = dsp.butter(6, cutoff, fs=sr, btype="low", output="sos")
    return dsp.sosfiltfilt(sos, y).astype(np.float32)


def pitch_shift(y: np.ndarray, sr: int, semitones: float) -> np.ndarray:
    if semitones == 0:
        return y
    if _HAVE_PRAAT and len(y) > sr * 0.05:
        try:
            snd = parselmouth.Sound(y.astype(np.float64), sampling_frequency=sr)
            man = _praat(snd, "To Manipulation", 0.01, 55.0, 700.0)
            tier = _praat(man, "Extract pitch tier")
            _praat(tier, "Multiply frequencies", 2 ** (semitones / 12.0), snd.xmin, snd.xmax)
            _praat([man, tier], "Replace pitch tier")
            out = _praat(man, "Get resynthesis (overlap-add)")
            return np.asarray(out.values[0], dtype=np.float32)
        except Exception:
            pass
    return librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitones).astype(np.float32)


def rate_tape(y: np.ndarray, rate: float) -> np.ndarray:
    """Kaset hızı: per değişimiyle birlikte süre değişir (doğal)."""
    if rate == 1.0 or len(y) < 32:
        return y
    n = len(y)
    return librosa.resample(y, orig_sr=n, target_sr=int(n / rate)).astype(np.float32)


def formant_convert(y: np.ndarray, sr: int, ratio: float) -> np.ndarray:
    """Ses yolu uzunluğu dönüşümü. ratio>1 → daha kalın/erkek (F0 ve formantlar ~1/ratio),
    ratio<1 → daha ince/kadın. Süre eski haline döndürülür."""
    if ratio == 1.0 or len(y) < 64:
        return y
    n = len(y)
    y1 = librosa.resample(y, orig_sr=n, target_sr=int(n * ratio))
    y2 = librosa.effects.time_stretch(y1, rate=ratio)
    m = min(len(y2), n)
    out = np.zeros(n, dtype=np.float32)
    out[:m] = y2[:m]
    return out


def _vibrato(y: np.ndarray, sr: int, cents: float, hz: float) -> np.ndarray:
    if cents <= 0 or hz <= 0 or len(y) == 0:
        return y
    t = np.arange(len(y)) / sr
    depth = 2 ** (cents / 1200.0) - 1.0
    mod = 1.0 + depth * np.sin(2 * np.pi * hz * t)
    idx = np.cumsum(mod) / mod.mean()
    idx = idx / idx[-1] * (len(y) - 1)
    return np.interp(np.arange(len(y)), idx, y).astype(np.float32)


def _tremolo(y: np.ndarray, sr: int, db: float, hz: float) -> np.ndarray:
    if db <= 0 or hz <= 0:
        return y
    t = np.arange(len(y)) / sr
    mod = 1.0 + (10 ** (db / 20) - 1.0) * 0.5 * (1 + np.sin(2 * np.pi * hz * t))
    return y * mod.astype(np.float32)


def add_breathiness(y: np.ndarray, sr: int, amount: float) -> np.ndarray:
    if amount <= 0:
        return y
    noise = np.random.default_rng(0).standard_normal(len(y)).astype(np.float32) * 0.008
    # ince, temiz bir nefes: 1.5-6 kHz bant, düşük genlik
    sos = dsp.butter(2, [1500, 6000], fs=sr, btype="bandpass", output="sos")
    noise = dsp.sosfiltfilt(sos, noise)
    return (y * (1 - amount * 0.3) + noise * amount).astype(np.float32)


def humanize(y: np.ndarray, sr: int, amount: float = 1.0) -> np.ndarray:
    """AI likini kıran küçük sapmalar: mikro vibrato, yumuşak tavan, dither."""
    if amount <= 0:
        return y
    rng = np.random.default_rng(42)
    y = _vibrato(y, sr, 4.0 * amount, 5.0)
    # çok hafif doğal oda yansıması (20 ms, -26 dB)
    delay = int(sr * 0.02)
    y2 = np.zeros_like(y)
    y2[delay:] = y[:-delay] * 0.05
    y = y + y2
    # dither
    y = y + rng.standard_normal(len(y)).astype(np.float32) * (1e-4 * amount)
    peak = np.max(np.abs(y)) + 1e-8
    if peak > 1.0:
        y = y / peak
    return y.astype(np.float32)


def apply_prosody(y: np.ndarray, sr: int, p: Prosody, voice: Voice | None = None) -> np.ndarray:
    y = _to_mono(y)
    if len(y) == 0 or np.sqrt(np.mean(y ** 2)) < 1e-5:
        return y
    # Ses kanalı dönüşümü (voice)
    if voice is not None and voice.formant != 1.0:
        y = formant_convert(y, sr, voice.formant)
    # Hız: kaset usulü (duygu profili × ses profili)
    rate = p.rate * (voice.rate if voice else 1.0)
    y = rate_tape(y, rate)
    # Per
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
