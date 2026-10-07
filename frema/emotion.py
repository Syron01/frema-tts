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
    "kizgin": Prosody(pitch_semitones=2.5, rate=1.12, gain_db=4, brightness=2.0, tremolo_db=2.5, tremolo_hz=6, pause_scale=0.7),
    "mutlu": Prosody(pitch_semitones=2.0, rate=1.1, gain_db=2, brightness=1.5, vibrato_cents=15, pause_scale=0.9),
    "uzgun": Prosody(pitch_semitones=-2.5, rate=0.88, gain_db=-2, brightness=-2.5, vibrato_cents=25, vibrato_hz=4.5, pause_scale=1.4),
    "fisilti": Prosody(pitch_semitones=1.0, rate=0.92, gain_db=-6, brightness=-4, breathiness=0.85, pause_scale=1.2),
    "bagir": Prosody(pitch_semitones=4.0, rate=1.15, gain_db=8, brightness=4, tremolo_db=3, tremolo_hz=8, pause_scale=0.6),
    "sakin": Prosody(pitch_semitones=-1.0, rate=0.95, gain_db=0, brightness=-1, vibrato_cents=8, pause_scale=1.3),
    "heyecanlı": Prosody(pitch_semitones=3.0, rate=1.22, gain_db=3, brightness=2.5, vibrato_cents=20, tremolo_db=2, tremolo_hz=7, pause_scale=0.6),
    "yumuşak": Prosody(pitch_semitones=-1.5, rate=0.92, gain_db=-1, brightness=-3, vibrato_cents=10, breathiness=0.25, pause_scale=1.2),
    "güçlü": Prosody(pitch_semitones=-1.0, rate=1.0, gain_db=4, brightness=1, pause_scale=1.1),
    "anlatıcı": Prosody(pitch_semitones=-0.5, rate=0.97, gain_db=1, brightness=0.5, vibrato_cents=6, pause_scale=1.25),
    "haber": Prosody(pitch_semitones=0.5, rate=1.08, gain_db=2, brightness=2, pause_scale=0.9),
    "romantik": Prosody(pitch_semitones=-2.0, rate=0.85, gain_db=-1, brightness=-2, vibrato_cents=30, vibrato_hz=4, breathiness=0.3, pause_scale=1.4),
    "korkmuş": Prosody(pitch_semitones=3.5, rate=1.25, gain_db=0, brightness=1, vibrato_cents=35, vibrato_hz=7, pause_scale=0.7),
    "ciddi": Prosody(pitch_semitones=-1.5, rate=0.93, gain_db=1, brightness=-0.5, pause_scale=1.2),
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
