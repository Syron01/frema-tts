"""Duygu etiketleri ve prozodi dinamikleri: Doğal tonlama ve tempo.

Metin içine köşeli parantezle duygu etiketleri eklenir, örn:
    "[ciddi] Sayın dinleyiciler, [sakin] bu akşam özel bir konuğumuz var."

Yapay mikro-vibrato veya gürültü eklenmez; duygu ifadesi tempo (hız), duraklama süreleri,
gövde rezonansı ve dinamik seviye ile tamamen doğal biçimde sağlanır.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ALIASES = {
    "angry": "kizgin", "kızgın": "kizgin",
    "happy": "mutlu", "neşeli": "mutlu", "neşe": "mutlu",
    "sad": "uzgun", "üzgün": "uzgun", "hüzünlü": "uzgun",
    "whisper": "fisilti", "fısıltı": "fisilti",
    "shout": "bagir", "bağır": "bagir", "bağırış": "bagir",
    "calm": "sakin",
    "excited": "heyecanlı",
    "soft": "yumuşak",
    "strong": "güçlü",
    "narrator": "anlatıcı", "hikaye": "anlatıcı",
    "news": "haber",
    "romantic": "romantik",
    "scared": "korkmuş",
    "serious": "ciddi",
}


@dataclass
class Prosody:
    warmth_delta: float = 0.0     # dB gövde/tokluk değişimi
    presence_delta: float = 0.0   # dB netlik/artikülasyon değişimi
    speed_factor: float = 1.0     # Hız çarpanı (<1 daha ağırbaşlı, >1 daha enerjik)
    gain_db: float = 0.0          # Ses düzeyi (dB)
    pause_scale: float = 1.0      # Virgül/nokta duraklama uzunluğu çarpanı
    # Geriye dönük uyumluluk alanları
    pitch_semitones: float = 0.0
    rate: float = 1.0
    brightness: float = 0.0
    vibrato_cents: float = 0.0
    vibrato_hz: float = 5.0
    tremolo_db: float = 0.0
    tremolo_hz: float = 4.0
    breathiness: float = 0.0


EMOTIONS: dict[str, Prosody] = {
    "sakin": Prosody(warmth_delta=1.0, speed_factor=0.92, pause_scale=1.2, gain_db=0.0),
    "ciddi": Prosody(warmth_delta=1.8, presence_delta=0.8, speed_factor=0.90, pause_scale=1.2, gain_db=1.0),
    "anlatıcı": Prosody(warmth_delta=2.2, presence_delta=0.8, speed_factor=0.88, pause_scale=1.3, gain_db=1.0),
    "güçlü": Prosody(warmth_delta=2.0, presence_delta=1.0, speed_factor=0.94, pause_scale=1.1, gain_db=2.0),
    "mutlu": Prosody(warmth_delta=-0.5, presence_delta=1.0, speed_factor=1.02, pause_scale=0.95, gain_db=1.2),
    "haber": Prosody(warmth_delta=0.5, presence_delta=1.8, speed_factor=1.02, pause_scale=0.9, gain_db=1.5),
    "heyecanlı": Prosody(warmth_delta=0.0, presence_delta=1.5, speed_factor=1.08, pause_scale=0.8, gain_db=2.0),
    "kizgin": Prosody(warmth_delta=0.5, presence_delta=2.0, speed_factor=1.05, pause_scale=0.85, gain_db=2.5),
    "uzgun": Prosody(warmth_delta=1.2, presence_delta=-1.0, speed_factor=0.88, pause_scale=1.3, gain_db=-1.5),
    "romantik": Prosody(warmth_delta=1.8, presence_delta=-0.5, speed_factor=0.86, pause_scale=1.4, gain_db=-0.5),
    "yumuşak": Prosody(warmth_delta=1.5, presence_delta=-0.5, speed_factor=0.90, pause_scale=1.2, gain_db=-0.5),
    "fisilti": Prosody(warmth_delta=-1.0, presence_delta=-1.0, speed_factor=0.90, pause_scale=1.2, gain_db=-4.0),
    "bagir": Prosody(warmth_delta=1.0, presence_delta=2.5, speed_factor=1.08, pause_scale=0.8, gain_db=3.5),
    "korkmuş": Prosody(warmth_delta=-0.5, presence_delta=1.0, speed_factor=1.06, pause_scale=0.85, gain_db=0.5),
}

NEUTRAL = Prosody()

_TAG_RE = re.compile(r"\[([^\[\]]+)\]")


def canon(name: str) -> str:
    n = name.strip().lower()
    return ALIASES.get(n, n)


def split_segments(text: str) -> list[tuple[str | None, str]]:
    """(etiket, metin) parçaları. Etiket None ise nötr."""
    parts: list[tuple[str | None, str]] = []
    pos = 0
    current: str | None = None
    for m in _TAG_RE.finditer(text):
        chunk = text[pos:m.start()]
        if chunk.strip():
            parts.append((current, chunk))
        current = canon(m.group(1))
        pos = m.end()
    tail = text[pos:]
    if tail.strip():
        parts.append((current, tail))
    if not parts:
        parts.append((None, text))
    return parts


def prosody_for(tag: str | None) -> Prosody:
    if tag is None:
        return NEUTRAL
    return EMOTIONS.get(tag, NEUTRAL)
