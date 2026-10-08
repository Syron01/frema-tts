"""Frema: Yüksek kaliteli, insansı ve tok ses üretim katmanı.

Özellikler:
- Birincil Motor: Trendyol-TTS (2.38B VoxCPM2) — Sıfır robotiklik, tok ve net göğüs tonu,
  tamamen doğal akış, UTMOS 3.83 (ElevenLabs ve Gemini düzeyinin üstünde insan doğallığı).
- İkincil Motor: EMA-TTS (65M Flow-Matching) — Hızlı motor, süre ölçekleme (hız kontrolü)
  ve stüdyo akustik zarfıyla güçlendirilmiş, robotiklikten arındırılmış.
- Akustik Sınır Koruması (Envelope Guard): Cümlenin başındaki ilk ses ve sonundaki son
  karakter asla kesilmez veya söndürülmez.
- Stüdyo Mastering: -16 LUFS yayın normalizasyonu, -1.0 dBTP limitör, doğrudan .mp3 çıktısı.
"""

from __future__ import annotations

import numpy as np
import torch

from .emotion import split_segments, prosody_for
from .voices import get_voice, Voice
from .processing import (
    apply_prosody,
    apply_tok_clarity_eq,
    pad_and_envelope,
    to_mastered_stereo,
    master_audio,
    save_audio,
)

_to_stereo = to_mastered_stereo

_TRENDYOL = None
_EMATTS = None


def _trendyol(device: str = "cuda"):
    global _TRENDYOL
    if _TRENDYOL is None:
        from voxcpm import VoxCPM
        dev = device if (torch.cuda.is_available() and device.startswith("cuda")) else "cpu"
        _TRENDYOL = VoxCPM.from_pretrained(
            "Trendyol/Trendyol-TTS",
            load_denoiser=False,
            optimize=True,
        )
    return _TRENDYOL


def _ema_tts(device: str = "cuda"):
    global _EMATTS
    if _EMATTS is None:
        import sys
        sys.path.insert(0, "ema-tts")
        from inference import EmaTTS
        dev = device if (torch.cuda.is_available() and device.startswith("cuda")) else "cpu"
        _EMATTS = EmaTTS.from_pretrained("ema-tts/ckpt", device=dev)
    return _EMATTS


class Frema:
    def __init__(
        self,
        voice: str = "varsayilan",
        speed: float = 1.0,
        engine: str = "trendyol",
        device: str | None = None,
    ):
        """Frema ses sentezleyici.

        Args:
            voice: Ses profili adı ('varsayilan', 'tok_erkek', 'derin_anlatici', 'podcast', 'haber_spikeri', 'kadin', 'yumusak').
            speed: Konuşma hızı çarpanı (1.0 = doğal, 0.9 = sakin/tok, 1.1 = seri).
            engine: Sentez motoru:
                    - 'trendyol': 2.38B VoxCPM2 tabanlı, en insansı ve tok ses (varsayılan).
                    - 'ematts': 65M hafif ve ultra hızlı akış motoru.
            device: 'cuda' veya 'cpu' (varsayılan: otomatik GPU tespiti).
        """
        self.voice = get_voice(voice)
        self.speed = speed
        self.engine = engine.strip().lower()
        if self.engine in ("ema", "fast"):
            self.engine = "ematts"
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    def set_voice(self, name: str) -> None:
        self.voice = get_voice(name)

    def say(
        self,
        text: str,
        path: str | None = None,
        voice: str | None = None,
        seed: int | None = None,
        speed: float | None = None,
        steps: int | None = None,
        format: str = "MP3",
    ) -> tuple[np.ndarray, int]:
        """Metni sese dönüştürür ve stüdyo mastering uygulayarak döndürür/kaydeder.

        Args:
            text: Okunacak metin (isteğe bağlı [ciddi], [sakin], [mutlu] etiketleri içerebilir).
            path: Kaydedilecek dosya yolu (örn: 'cikti.mp3').
            voice: Özel ses profili adı.
            seed: Rastgelelik çekirdeği (tekrarlanabilir sonuçlar için).
            speed: Özel hız çarpanı.
            steps: Çıkarım adım sayısı.
            format: 'MP3' (varsayılan) veya 'WAV'.
        """
        v = get_voice(voice) if voice else self.voice
        base_speed = (speed if speed is not None else self.speed) * v.speed
        segments = split_segments(text)
        pieces: list[np.ndarray] = []
        sr = 48000

        for tag, chunk in segments:
            clean_chunk = chunk.strip()
            if not clean_chunk:
                continue

            p = prosody_for(tag)
            seg_speed = base_speed * p.speed_factor

            if self.engine == "trendyol":
                tts = _trendyol(device=self.device)
                timesteps = steps or 24
                # VoxCPM ile üretim
                wav = tts.generate(
                    clean_chunk,
                    cfg_value=2.0,
                    inference_timesteps=timesteps,
                    normalize=True,
                )
                y = np.asarray(wav, dtype=np.float32)
                sr = 48000
            else:
                tts = _ema_tts(device=self.device)
                sr = tts.sample_rate
                # Hız ve sınır güvenliği ile üretim
                wav = tts.say(
                    clean_chunk,
                    steps=steps,
                    seed=seed,
                    master=False,
                    speed=seg_speed,
                )
                y = np.asarray(wav, dtype=np.float32)

            # Ekolayzır ve dinamik ayarı
            y = apply_prosody(y, sr, p, voice=v)
            pieces.append(y)

            # Cümleler arasına doğal nefes/duraklama boşluğu (140-220 ms)
            pause_samples = int(sr * 0.16 * p.pause_scale)
            if pause_samples > 0:
                pieces.append(np.zeros(pause_samples, dtype=np.float32))

        if not pieces:
            audio = np.zeros(sr, dtype=np.float32)
        else:
            audio = np.concatenate(pieces)

        # 1. Stüdyo Tok ve Net EQ cilası
        audio = apply_tok_clarity_eq(
            audio,
            sr,
            warmth_db=v.warmth_db,
            presence_db=v.presence_db,
            air_db=v.air_db,
        )

        # 2. Akustik Sınır Koruması (ilk ve son harfin kırpılmasını önleyen tampon)
        audio = pad_and_envelope(
            audio,
            sr,
            lead_ms=70.0,
            trail_ms=180.0,
            fade_ms=25.0,
        )

        # 3. Stereo Master
        stereo = to_mastered_stereo(audio, sr)

        # 4. -16 LUFS Yayın Mastering & True-Peak Limiter
        stereo = master_audio(stereo, sr, target_lufs=-16.0, ceiling_db=-1.0)

        # 5. MP3 olarak kaydet
        if path:
            save_audio(stereo, sr, path, format=format)

        return stereo, sr

    def stream(self, text: str, voice: str | None = None):
        """Parça parça canlı akış."""
        v = get_voice(voice) if voice else self.voice
        for tag, chunk in split_segments(text):
            clean_chunk = chunk.strip()
            if not clean_chunk:
                continue
            p = prosody_for(tag)
            seg_speed = self.speed * v.speed * p.speed_factor
            tts = _ema_tts(device=self.device)
            part = tts.say(clean_chunk, speed=seg_speed, master=False)
            y = np.asarray(part, dtype=np.float32)
            y = apply_prosody(y, 48000, p, voice=v)
            yield y
