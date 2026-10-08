import numpy as np
import os
import tempfile

from frema.emotion import split_segments, prosody_for, EMOTIONS, canon
from frema.voices import VOICES, get_voice
from frema.processing import (
    apply_prosody,
    humanize,
    apply_tok_clarity_eq,
    pad_and_envelope,
    to_mastered_stereo,
    master_audio,
    save_audio,
)
from frema.core import _to_stereo


def test_emotion_split():
    parts = split_segments("[kızgın] Selam! [sakin] Tamam.")
    assert parts[0][0] == "kizgin"
    assert parts[1][0] == "sakin"
    assert "Selam" in parts[0][1]


def test_canon_aliases():
    assert canon("angry") == "kizgin"
    assert canon("fısıltı") == "fisilti"


def test_all_emotions_have_prosody():
    for name in EMOTIONS:
        p = prosody_for(name)
        assert p is not None


def test_voices():
    for name in VOICES:
        v = get_voice(name)
        assert v.name == name


def test_prosody_no_nan():
    sr = 48000
    t = np.arange(sr) / sr
    y = (0.1 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    out = apply_prosody(y, sr, prosody_for("mutlu"), voice=get_voice("varsayilan"))
    assert np.isfinite(out).all()
    assert out.dtype == np.float32


def test_stereo_shape():
    sr = 48000
    y = np.random.default_rng(0).standard_normal(sr).astype(np.float32) * 0.1
    s = _to_stereo(y, sr)
    assert s.shape == (sr, 2)
    assert np.isfinite(s).all()


def test_humanize():
    sr = 48000
    y = np.zeros(sr, dtype=np.float32)
    out = humanize(y, sr)
    assert out.shape == y.shape
    assert np.isfinite(out).all()


def test_pad_and_envelope_preserves_speech():
    sr = 48000
    sig = np.ones(sr, dtype=np.float32) * 0.5
    padded = pad_and_envelope(sig, sr, lead_ms=70.0, trail_ms=180.0, fade_ms=25.0)
    lead_n = int(sr * 0.07)
    trail_n = int(sr * 0.18)
    assert len(padded) == len(sig) + lead_n + trail_n
    # Speech region must be completely unattenuated
    assert np.allclose(padded[lead_n : lead_n + sr], sig)


def test_tok_clarity_eq():
    sr = 48000
    t = np.arange(sr) / sr
    sig = (0.2 * np.sin(2 * np.pi * 140 * t) + 0.1 * np.sin(2 * np.pi * 3200 * t)).astype(np.float32)
    out = apply_tok_clarity_eq(sig, sr, warmth_db=2.0, presence_db=2.0)
    assert len(out) == len(sig)
    assert np.isfinite(out).all()


def test_mp3_save():
    sr = 48000
    sig = np.zeros((sr, 2), dtype=np.float32)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name
    try:
        saved = save_audio(sig, sr, tmp_path, format="MP3")
        assert os.path.exists(saved)
        assert os.path.getsize(saved) > 0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
