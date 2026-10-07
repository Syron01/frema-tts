"""Frema: EMA Lightning üstüne duygu etiketleri, ses profilleri ve insanileştirme."""

from __future__ import annotations

import numpy as np
import soundfile as sf

from .emotion import split_segments, prosody_for
from .voices import get_voice, Voice
from .processing import apply_prosody

_EMA = None
_EMATTS = None


def _ema():
    global _EMA
    if _EMA is None:
        from ema_lightning import EMA
        _EMA = EMA()
    return _EMA


def _ema_tts():
    global _EMATTS
    if _EMATTS is None:
        import sys
        sys.path.insert(0, "ema-tts")
        from inference import EmaTTS
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _EMATTS = EmaTTS.from_pretrained("ema-tts/ckpt", device=device)
    return _EMATTS


def _to_stereo(y: np.ndarray, sr: int = 48000) -> np.ndarray:
    """Mono'yu doğal stereoya taşır: doğrudan yol iki kanalda birebir,
    genişlik her kanalda farklı kısa yansıma kuyruklarından gelir (faz çakışması yok)."""
    if y.ndim == 2:
        return y
    def tail(delays_gains):
        out = np.zeros_like(y)
        for d_ms, g in delays_gains:
            d = int(sr * d_ms / 1000)
            if d <= 0:
                out += y * g
            else:
                out[d:] += y[:-d] * g
        return out
    left = y + tail([(23, 0.10), (41, 0.05), (67, 0.03)])
    right = y + tail([(29, 0.10), (53, 0.05), (71, 0.03)])
    stereo = np.stack([left, right], axis=-1)
    peak = np.max(np.abs(stereo)) + 1e-8
    if peak > 0.98:
        stereo = stereo / peak * 0.98
    return stereo


class Frema:
    def __init__(self, voice: str = "varsayilan", speed: float = 1.0, engine: str = "ematts"):
        self.voice = get_voice(voice)
        self.speed = speed
        self.engine = engine

    def set_voice(self, name: str) -> None:
        self.voice = get_voice(name)

    def say(self, text: str, path: str | None = None, voice: str | None = None,
            seed: int | None = None, sample_rate: int = 48000) -> tuple[np.ndarray, int]:
        v = get_voice(voice) if voice else self.voice
        segments = split_segments(text)
        pieces: list[np.ndarray] = []
        sr = sample_rate
        for tag, chunk in segments:
            if self.engine == "ematts":
                tts = _ema_tts()
                wav = tts.say(chunk.strip(), seed=seed)
                sr = tts.sample_rate
                y = np.asarray(wav, dtype=np.float32)
            else:
                tts = _ema()
                speech = tts.say(chunk.strip(), seed=seed, sample_rate=sr,
                                 speed=self.speed) if seed is not None else tts.say(
                    chunk.strip(), sample_rate=sr, speed=self.speed)
                y = np.asarray(speech.audio, dtype=np.float32)
                sr = speech.sample_rate
            p = prosody_for(tag)
            y = apply_prosody(y, sr, p, voice=v)
            # 20 ms fade ile sınır tıklamalarını/kesilmelerini önle
            fade = min(int(sr * 0.02), len(y) // 4)
            if fade > 1:
                ramp = np.linspace(0, 1, fade, dtype=np.float32)
                y[:fade] *= ramp
                y[-fade:] *= ramp[::-1]
            pieces.append(y)
            gap = np.zeros(int(sr * 0.08), dtype=np.float32)
            pieces.append(gap)
        audio = np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)
        if path:
            audio = _to_stereo(audio, sr)
            sf.write(path, audio, sr, subtype="PCM_24")
        return audio, sr

    def stream(self, text: str, voice: str | None = None):
        """Parça parça (chunk) üretir; ilk ses hızlı gelir."""
        v = get_voice(voice) if voice else self.voice
        for tag, chunk in split_segments(text):
            for part in _ema().stream(chunk.strip(), speed=self.speed):
                y = np.asarray(part.audio, dtype=np.float32) if hasattr(part, "audio") else np.asarray(part, dtype=np.float32)
                p = prosody_for(tag)
                y = apply_prosody(y, 48000, p, voice=v)
                yield y
