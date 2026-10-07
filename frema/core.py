"""Frema: EMA Lightning üstüne duygu etiketleri, ses profilleri ve insanileştirme."""

from __future__ import annotations

import numpy as np
import soundfile as sf

from .emotion import split_segments, prosody_for
from .voices import get_voice, Voice
from .processing import apply_prosody

_EMA = None


def _ema():
    global _EMA
    if _EMA is None:
        from ema_lightning import EMA
        _EMA = EMA()
    return _EMA


class Frema:
    def __init__(self, voice: str = "erkek", speed: float = 1.0):
        self.voice = get_voice(voice)
        self.speed = speed

    def set_voice(self, name: str) -> None:
        self.voice = get_voice(name)

    def say(self, text: str, path: str | None = None, voice: str | None = None,
            seed: int | None = None, sample_rate: int = 48000) -> tuple[np.ndarray, int]:
        v = get_voice(voice) if voice else self.voice
        segments = split_segments(text)
        pieces: list[np.ndarray] = []
        sr = sample_rate
        for tag, chunk in segments:
            tts = _ema()
            speech = tts.say(chunk.strip(), seed=seed, sample_rate=sr,
                             speed=self.speed) if seed is not None else tts.say(
                chunk.strip(), sample_rate=sr, speed=self.speed)
            y = np.asarray(speech.audio, dtype=np.float32)
            p = prosody_for(tag)
            y = apply_prosody(y, speech.sample_rate, p, voice=v)
            pieces.append(y)
            # parçalar arası küçük nefes payı
            gap = np.zeros(int(speech.sample_rate * 0.08), dtype=np.float32)
            pieces.append(gap)
        audio = np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)
        if path:
            sf.write(path, audio, sr)
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
