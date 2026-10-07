"""Duygu etiketleri ve prozodi eşlemesi.

Metin içine ElevenLabs tarzı etiketler yazılır, örn:
    "[kızgın] Bu nasıl bir teklif böyle! [sakin] Hadi tekrar konuşalım."

Her etiket bir prozodi seti tanımlar: pitch kayması (semiton), hız çarpanı,
enerji kazancı (dB), spektral eğim, titreme (vibrato) miktarı.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# İsim -> kanonik etiket
ALIASES = {
    "angry": "kizgin", "kızgın": "kizgin",
    "happy": "mutlu", "neşeli": "mutlu", "neşe": "mutlu",
    "sad": "uzgun", "üzgün": "uzgun", "hüzünlü": "uzgun",
    "whisper": "fisilti", "fısıltı": "fisilti", "fisilti": "fisilti",
    "shout": "bagir", "bağır": "bagir", "bağırış": "bagir",
    "calm": "sakin",
    "excited": "heyecanlı", "heyecanlı": "heyecanlı",
    "soft": "yumuşak", "yumuşak": "yumuşak",
    "strong": "güçlü", "güçlü": "güçlü",
    "narrator": "anlatıcı", "anlatıcı": "anlatıcı", "hikaye": "anlatıcı",
    "news": "haber", "haber": "haber",
    "romantic": "romantik", "romantik": "romantik",
    "scared": "korkmuş", "korkmuş": "korkmuş",
    "serious": "ciddi", "ciddi": "ciddi",
}


@dataclass
class Prosody:
    pitch_semitones: float = 0.0
    rate: float = 1.0
    gain_db: float = 0.0
    brightness: float = 0.0   # spektral eğim dB/oct (+ parlak, - boğuk)
    vibrato_cents: float = 0.0
    vibrato_hz: float = 5.5
    tremolo_db: float = 0.0
    tremolo_hz: float = 4.0
    # duraksama uzunluğu çarpanı (virgül/nokta)
    pause_scale: float = 1.0
    breathiness: float = 0.0   # fısıltı miktarı 0..1


EMOTIONS: dict[str, Prosody] = {
    "kizgin": Prosody(pitch_semitones=1.5, rate=1.08, gain_db=3, brightness=1.5, tremolo_db=1.5, tremolo_hz=6, pause_scale=0.8),
    "mutlu": Prosody(pitch_semitones=1.0, rate=1.05, gain_db=1.5, brightness=1.0, vibrato_cents=8, pause_scale=0.95),
    "uzgun": Prosody(pitch_semitones=-1.0, rate=0.93, gain_db=-1.5, brightness=-1.5, vibrato_cents=15, vibrato_hz=4.5, pause_scale=1.3),
    "fisilti": Prosody(pitch_semitones=0.5, rate=0.95, gain_db=-5, brightness=-3, breathiness=0.6, pause_scale=1.1),
    "bagir": Prosody(pitch_semitones=2.5, rate=1.1, gain_db=6, brightness=3, tremolo_db=2, tremolo_hz=8, pause_scale=0.7),
    "sakin": Prosody(pitch_semitones=-0.5, rate=0.97, gain_db=0, brightness=-0.5, vibrato_cents=4, pause_scale=1.2),
    "heyecanlı": Prosody(pitch_semitones=1.5, rate=1.12, gain_db=2.5, brightness=1.5, vibrato_cents=8, tremolo_db=1, tremolo_hz=7, pause_scale=0.8),
    "yumuşak": Prosody(pitch_semitones=-0.5, rate=0.95, gain_db=-0.5, brightness=-1.5, vibrato_cents=5, breathiness=0.2, pause_scale=1.2),
    "güçlü": Prosody(pitch_semitones=-0.5, rate=1.0, gain_db=3, brightness=0.5, pause_scale=1.1),
    "anlatıcı": Prosody(pitch_semitones=0.0, rate=1.0, gain_db=1, brightness=0.5, vibrato_cents=3, pause_scale=1.2),
    "haber": Prosody(pitch_semitones=0.5, rate=1.08, gain_db=2, brightness=2, pause_scale=0.9),
    "romantik": Prosody(pitch_semitones=-0.5, rate=0.9, gain_db=-0.5, brightness=-1, vibrato_cents=15, vibrato_hz=4, breathiness=0.25, pause_scale=1.3),
    "korkmuş": Prosody(pitch_semitones=2.0, rate=1.15, gain_db=0, brightness=0.5, vibrato_cents=20, vibrato_hz=7, pause_scale=0.8),
    "ciddi": Prosody(pitch_semitones=0.0, rate=1.0, gain_db=1, brightness=0.5, pause_scale=1.2),
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
