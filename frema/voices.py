"""Ses profilleri. EMA tek ses üretir; profiller pitch/EQ ile
erkek/kadın/karakter sesleri türetir."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Voice:
    name: str
    pitch_semitones: float = 0.0
    brightness: float = 0.0
    gain_db: float = 0.0
    rate: float = 1.0
    breathiness: float = 0.0
    lowpass_hz: float | None = None  # erkekliği derinleştirmek için hafif lowpass


VOICES: dict[str, Voice] = {
    "varsayilan": Voice("varsayilan"),
    "erkek": Voice("erkek", pitch_semitones=-4.0, brightness=-1.5, gain_db=1.0, lowpass_hz=5200),
    "derin_erkek": Voice("derin_erkek", pitch_semitones=-6.5, brightness=-2.5, gain_db=1.5, lowpass_hz=4200),
    "genc_erkek": Voice("genc_erkek", pitch_semitones=-2.0, brightness=0.5, rate=1.05),
    "anlatici_erkek": Voice("anlatici_erkek", pitch_semitones=-3.0, brightness=-1.0, gain_db=1.0, rate=0.97, lowpass_hz=5600),
    "kadin": Voice("kadin", pitch_semitones=3.5, brightness=2.0, gain_db=-0.5),
    "yumusak_kadin": Voice("yumusak_kadin", pitch_semitones=2.5, brightness=0.5, breathiness=0.3),
    "robot": Voice("robot", pitch_semitones=-1.0, brightness=-2, gain_db=2, rate=1.0, lowpass_hz=3500),
    "kaptan": Voice("kaptan", pitch_semitones=-5.0, brightness=-1.0, gain_db=3, rate=0.93, lowpass_hz=4500),
}


def get_voice(name: str) -> Voice:
    key = name.strip().lower()
    if key not in VOICES:
        raise KeyError(f"Bilinmeyen ses: {name}. Seçenekler: {', '.join(VOICES)}")
    return VOICES[key]
