"""Ses profilleri. EMA tek ses üretir; profiller formant/per/EQ ile
erkek/kadın/karakter sesleri türetir."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Voice:
    name: str
    pitch_semitones: float = 0.0
    formant: float = 1.0       # >1 daha kalın (erkek), <1 daha ince (kadın)
    brightness: float = 0.0
    gain_db: float = 0.0
    rate: float = 1.0
    breathiness: float = 0.0
    lowpass_hz: float | None = None


VOICES: dict[str, Voice] = {
    "varsayilan": Voice("varsayilan"),
    "erkek": Voice("erkek", pitch_semitones=-1.5, formant=1.0, brightness=-0.3, gain_db=1.0),
    "derin_erkek": Voice("derin_erkek", pitch_semitones=-2.5, formant=1.03, brightness=-1.0, gain_db=1.5),
    "genc_erkek": Voice("genc_erkek", pitch_semitones=-0.5, formant=1.0, brightness=0.3, rate=1.05),
    "anlatici_erkek": Voice("anlatici_erkek", pitch_semitones=-1.0, formant=1.0, brightness=0.0, gain_db=1.0, rate=0.97),
    "kadin": Voice("kadin", pitch_semitones=1.5, formant=1.0, brightness=1.0, gain_db=-0.5),
    "yumusak_kadin": Voice("yumusak_kadin", pitch_semitones=1.0, formant=1.0, brightness=0.0, breathiness=0.15),
    "robot": Voice("robot", pitch_semitones=-1.0, formant=1.0, brightness=-2, gain_db=2),
    "kaptan": Voice("kaptan", pitch_semitones=-2.0, formant=1.03, brightness=-0.5, gain_db=3, rate=0.97),
}


def get_voice(name: str) -> Voice:
    key = name.strip().lower()
    if key not in VOICES:
        raise KeyError(f"Bilinmeyen ses: {name}. Seçenekler: {', '.join(VOICES)}")
    return VOICES[key]
