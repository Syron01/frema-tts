import numpy as np

from frema.emotion import split_segments, prosody_for, EMOTIONS, canon
from frema.voices import VOICES, get_voice
from frema.processing import apply_prosody, humanize
from frema.core import _to_stereo


def test_emotion_split():
    parts = split_segments("[kızgın] Selam! [sakin] Tamam.")
    assert parts[0][0] == "kizgin"
    assert parts[1][0] == "sakin"
    assert "Selam" in parts[0][1]


def test_canon_aliases():
    assert canon("angry") == "kizgin"
    assert canon("FıSıLTı".lower()) in ("fisilti", "fisıltı", "fisilti")


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
    y = 0.1 * np.sin(2 * np.pi * 220 * t).astype(np.float32)
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
