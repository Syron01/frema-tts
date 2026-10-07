# Frema ⚡

**Frema**, Türkçe'nin en güçlü açık TTS modeli **EMA-TTS (65M)** üzerine kurulu; **duygu etiketli**, **ses profilli** ve **insanileştirilmiş** bir açık kaynak TTS katmanıdır. Tamamen offline çalışır, API anahtarı istemez.

[![Lisans](https://img.shields.io/badge/lisans-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Model](https://img.shields.io/badge/motor-EMA--TTS--65M-green)](https://huggingface.co/canberkkkkkk/ema-tts)

---

## 🎧 Ses Örnekleri

> Dosyalara tıklayınca GitHub oynatıcısında dinleyebilirsin.

| Örnek | Dosya | Duygular / Ses |
|---|---|---|
| Diyalog | [replik_diyalog.wav](examples/replik_diyalog.wav) | `[kızgın]` → `[sakin]` |
| Dublaj | [dublaj_kadin.wav](examples/dublaj_kadin.wav) | `[romantik]` → `[üzgün]`, kadın |
| Haber bülteni | [haber_spikeri.wav](examples/haber_spikeri.wav) | `[haber]` |
| Fısıltı & bağırış | [fisilti_bagir.wav](examples/fisilti_bagir.wav) | `[fısıltı]` → `[bağır]` |
| Anlatıcı | [replik_anlatici.wav](examples/replik_anlatici.wav) | `[ciddi]` → `[mutlu]` |
| Derin erkek | [derin_erkek_ciddi.wav](examples/derin_erkek_ciddi.wav) | `[ciddi]` + `[güçlü]` |
| Kadın romantik | [kadin_romantik.wav](examples/kadin_romantik.wav) | `[romantik]` |
| Etiket karışımı | [test_duygu.wav](examples/test_duygu.wav) | `[mutlu]` `[ciddi]` `[kızgın]` |

## ✨ Özellikler

- 🧠 **Motor: EMA-TTS 65M** — Türkçe'nin en güçlü açık modeli (3.0% WER, ElevenLabs'e yakın doğruluk)
- 🎭 **Duygu etiketleri** — ElevenLabs tarzı `[kızgın]`, `[fısıltı]`, `[heyecanlı]` …
- 🎙️ **8 ses profili** — `erkek`, `derin_erkek`, `anlatici_erkek`, `kadin`, `yumusak_kadin`, `genc_erkek`, `robot`, `kaptan`
- 🧹 **Temiz insanileştirme** — PSOLA per kaydırma, kısa yankı, dither. Faz vokoderi kullanılmaz.
- 🎧 **48 kHz PCM-24 stereo** — tek doğrudan yol + stereo kıyılı yankılar (faz güvenli)
- 💻 **Tamamen yerel** — GPU veya CPU, hiçbir veri dışarı çıkmaz

## 🚀 Kurulum

```bash
pip install ema-lightning librosa soundfile scipy praat-parselmouth voxcpm pyloudnorm
git clone --depth 1 https://huggingface.co/canberkkkkkk/ema-tts
git clone https://github.com/Syron01/frema-tts.git
cd frema-tts
pip install -e .
```

EMA-TTS checkpoint'ı ilk çalıştırmada `ema-tts/ckpt` klasörüne indirilir (~250 MB).

## 🎬 Hızlı Başlangıç

```python
from frema import Frema

f = Frema(voice="varsayilan")          # en temiz çıktı
f.say("[mutlu] Merhaba! [ciddi] Hadi başlayalım.", path="ornek.wav")
```

```bash
python -m frema.cli "[romantik] Gecenin sessizliğinde yıldızlar parlıyordu." -v kadin -o gece.wav
python -m frema.cli --list            # sesler
python -m frema.cli --list-emotions   # duygular
```

## 🎭 Duygu Etiketleri

Metin içine köşeli parantezle yazılır; o noktadan itibaren geçerlidir.

| Etiket | Etki |
|---|---|
| `[kızgın]` | tiz, hızlı, parlak, titrek |
| `[mutlu]` | tiz, hızlı, canlı |
| `[üzgün]` | pes, yavaş, boğuk, titrek |
| `[fısıltı]` | nefesli, alçak, yavaş |
| `[bağır]` | çok tiz, yüksek, parlak |
| `[sakin]` | hafif pes, yavaş, dingin |
| `[heyecanlı]` | tiz, çok hızlı, enerjik |
| `[yumuşak]` | pes, yavaş, nefesli |
| `[güçlü]` | yüksek, net |
| `[anlatıcı]` | hikâye tonu, yavaş ve derin |
| `[haber]` | spikere yakın, hızlı ve net |
| `[romantik]` | pes, yavaş, nefesli, titrek |
| `[korkmuş]` | tiz, titrek, hızlı |
| `[ciddi]` | pes, ölçülü |

İngilizce takma adlar: `[angry]`, `[happy]`, `[whisper]`, `[sad]`, `[calm]` …

## 🎙️ Ses Profilleri

| Profil | Açıklama |
|---|---|
| `varsayilan` | ham EMA-TTS sesi (önerilen) |
| `erkek` | hafif kalın (pitch ↓2.5 st) |
| `derin_erkek` | daha pes (pitch ↓4 st) |
| `genc_erkek` | daha ince, hızlı |
| `anlatici_erkek` | anlatıcı için dengeli |
| `kadin` | hafif ince (pitch ↑2 st) |
| `yumusak_kadin` | nefesli kadın tonu |
| `robot` | per düzleştirilmiş lo-fi |
| `kaptan` | derin ve otoriter |

## 🌊 Canlı Akış

```python
f = Frema(voice="anlatici_erkek")
for chunk in f.stream("[sakin] Merhaba, nasılsın?"):
    ...  # oynatıcıya ver
```

## ⏱️ Hız

```bash
python benchmark.py
```

| Donanım | RTF (Lightning) | Not |
|---|---|---|
| CPU | ~1.0× gerçek zaman | EMA-TTS CPU'da yavaş olabilir |
| RTX 5060 (EMA-TTS) | ~0.3–0.6× gerçek zaman | GPU önerilir |

## 🔧 Nasıl Çalışır?

1. **Motor** — EMA-TTS 65M; normalizer + flow-matching DiT + AudioVAE2 codec.
2. **Prozodi hattı** — her duygu etiketi için PSOLA per kaydırma, kaset usulü tempo, kazanç, spektral eğim, vibrato/tremolo. Faz vokoderi kullanılmaz.
3. **Ses profilleri** — ince PSOLA per + EQ + hafif formant denetimi.
4. **İnsanileştirme** — mikro vibrato, kısa yankı (stereo kıyılı), dither.
5. **Master** — 48 kHz PCM-24 stereo, -1 dBTP tavan.

## 🧪 Test

```bash
python -m pytest tests
```

## 📁 Proje Yapısı

```
frema/
├── core.py        # Frema sınıfı: say() / stream()
├── emotion.py     # duygu etiketleri ve prozodi tablosu
├── voices.py      # ses profilleri
├── processing.py  # PSOLA, tempo, EQ, vibrato, insanileştirme
└── cli.py         # komut satırı
examples/          # örnek .wav'ler
tests/             # birim testleri
benchmark.py       # hız ölçümü
```

## ⚖️ Lisans

Apache-2.0. EMA-TTS, EMA Lightning ve normalizer-tr ile uyumludur. Ticari kullanıma uygundur.

> Motor: https://huggingface.co/canberkkkkkk/ema-tts · Hızlı alternatif: https://huggingface.co/canberkkkkkk/ema-lightning
