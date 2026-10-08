"""Ses profilleri: Stüdyo akustik karakterleri ve EQ eğrileri."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Voice:
    name: str
    warmth_db: float = 0.0       # >0 daha tok/sıcak göğüs rezonansı (dB)
    presence_db: float = 0.0     # >0 daha net/belirgin diksiyon (dB)
    air_db: float = 0.0          # >0 ipeksi stüdyo havası (dB)
    speed: float = 1.0           # Hız çarpanı (<1 daha sakin ve tok, >1 daha seri)
    gain_db: float = 0.0
    reference_wav: str | None = None


VOICES: dict[str, Voice] = {
    "varsayilan": Voice("varsayilan", warmth_db=1.2, presence_db=0.8, speed=0.95),
    "tok_erkek": Voice("tok_erkek", warmth_db=2.5, presence_db=1.2, air_db=0.5, speed=0.92, gain_db=1.0),
    "derin_anlatici": Voice("derin_anlatici", warmth_db=3.5, presence_db=1.5, air_db=0.5, speed=0.88, gain_db=1.5),
    "podcast": Voice("podcast", warmth_db=2.0, presence_db=1.2, air_db=1.0, speed=0.93),
    "haber_spikeri": Voice("haber_spikeri", warmth_db=0.5, presence_db=2.2, air_db=1.5, speed=1.02),
    "kadin": Voice("kadin", warmth_db=-0.8, presence_db=1.5, air_db=2.0, speed=0.96),
    "yumusak": Voice("yumusak", warmth_db=1.5, presence_db=-0.5, air_db=0.5, speed=0.90, gain_db=-0.5),
}


def get_voice(name: str) -> Voice:
    key = name.strip().lower()
    aliases = {
        "erkek": "tok_erkek",
        "derin_erkek": "derin_anlatici",
        "anlatici_erkek": "derin_anlatici",
        "genc_erkek": "haber_spikeri",
        "yumusak_kadin": "yumusak",
    }
    key = aliases.get(key, key)
    if key not in VOICES:
        raise KeyError(f"Bilinmeyen ses: {name}. Seçenekler: {', '.join(VOICES)}")
    return VOICES[key]
