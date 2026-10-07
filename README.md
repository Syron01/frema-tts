# Frema ⚡

**Frema**, [EMA Lightning](https://huggingface.co/canberkkkkkk/ema-lightning) üzerine kurulu, Türkçe odaklı, **duygu etiketli**, **ses profilli** ve **insanileştirilmiş** açık kaynaklı bir metinden sese (TTS) katmanıdır.

- 🎭 ElevenLabs tarzı duygu etiketleri: `[kızgın]`, `[fısıltı]`, `[heyecanlı]` …
- 🎙️ 8 farklı ses profili: `erkek`, `derin_erkek`, `anlatıcı_erkek`, `kadın` …
- 🧹 "AI likini" kıran insanileştirme: mikro vibrato, yumuşak tavan, dithering
- ⚡ Akış (stream) desteği — ilk ses ~100 ms
- 💻 CPU'da çalışır, tamamen offline, ~34 MB model

## Kurulum

```bash
pip install ema-lightning librosa soundfile scipy
```

## Hızlı Başlangıç

```python
from frema import Frema

f = Frema(voice="erkek")
f.say(
    "[mutlu] Merhaba! [ciddi] Bu bir test. [kızgın] Hızlan!",
    path="ornek.wav",
)
```

## Duygu Etiketleri

Metin içine köşeli parantezle yazılır, o noktadan itibaren geçerlidir:

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

İngilizce takma adlar da çalışır: `[angry]`, `[happy]`, `[whisper]`, `[sad]` …

## Ses Profilleri

| Profil | Açıklama |
|---|---|
| `erkek` | varsayılan erkek tonu (pitch ↓4 st) |
| `derin_erkek` | daha kalın (pitch ↓6.5 st) |
| `genc_erkek` | daha ince, hızlı |
| `anlatici_erkek` | anlatıcı için dengeli |
| `kadin` | kadın tonu (pitch ↑3.5 st) |
| `yumusak_kadin` | nefesli kadın tonu |
| `robot` | lo-fi robot |
| `kaptan` | derin ve otoriter |

```python
f = Frema(voice="derin_erkek")
```

## CLI

```bash
python -m frema.cli "[mutlu] Selam!" -v erkek -o selam.wav
python -m frema.cli --list
python -m frema.cli --list-emotions
```

## Akış (Düşük Gecikme)

```python
for chunk in f.stream("[sakin] Merhaba, nasılsın?"):
    play(chunk)  # kendi oynatıcın
```

## Hız Testi

```bash
python benchmark.py
```

## Nasıl Geliştirildi?

Frema, EMA Lightning'in 48 kHz mono çıktısını alır ve üzerine:

1. **Prozodi hattı** — her duygu etiketi için pitch kaydırma (semiton), zaman uzatma,
   kazanç, spektral eğim (parlaklık), vibrato ve tremolo uygular.
2. **Ses profilleri** — temel sesi pitch/EQ ile erkek, derin, kadın, robot gibi
   farklı karakterlere dönüştürür.
3. **İnsanileştirme** — mikro vibrato, yumuşak yüksek frekans tavanı ve düşük
   genlikli dithering ekleyerek "AI likini" azaltır.

## Lisans

Apache-2.0 (EMA Lightning ve normalizer-tr ile uyumlu).

## Örnekler

- `examples/test_duygu.wav` — duygu etiketli örnek
- `benchmark.py` — hız ölçümü

> EMA Lightning'in orijinal sayfası: https://huggingface.co/canberkkkkkk/ema-lightning
