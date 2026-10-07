# Frema ⚡

**Frema**, [EMA Lightning](https://huggingface.co/canberkkkkkk/ema-lightning) üzerine kurulu, Türkçe odaklı, **duygu etiketli**, **ses profilli** ve **insanileştirilmiş** açık kaynaklı bir metinden sese (TTS) katmanıdır. Tamamen offline çalışır, API anahtarı istemez.

[![Lisans](https://img.shields.io/badge/lisans-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Model](https://img.shields.io/badge/model-~34%20MB-green)](https://huggingface.co/canberkkkkkk/ema-lightning)

---

## 🎧 Ses Örnekleri

> Dosyalara tıklayınca GitHub oynatıcısında dinleyebilirsin.

| Örnek | Dosya | Duygular / Ses |
|---|---|---|
| Diyalog | [replik_diyalog.wav](examples/replik_diyalog.wav) | `[kızgın]` → `[sakin]`, erkek |
| Dublaj | [dublaj_kadin.wav](examples/dublaj_kadin.wav) | `[romantik]` → `[üzgün]`, kadın |
| Haber bülteni | [haber_spikeri.wav](examples/haber_spikeri.wav) | `[haber]`, erkek |
| Fısıltı & bağırış | [fisilti_bagir.wav](examples/fisilti_bagir.wav) | `[fısıltı]` → `[bağır]` |
| Anlatıcı | [replik_anlatici.wav](examples/replik_anlatici.wav) | `[ciddi]` → `[mutlu]` |
| Derin erkek | [derin_erkek_ciddi.wav](examples/derin_erkek_ciddi.wav) | `[ciddi]` + `[güçlü]` |
| Kadın romantik | [kadin_romantik.wav](examples/kadin_romantik.wav) | `[romantik]` |
| Etiket karışımı | [test_duygu.wav](examples/test_duygu.wav) | `[mutlu]` `[ciddi]` `[kızgın]` |

---

## ✨ Neden Frema?

- 🎭 **Duygu etiketleri** — ElevenLabs tarzı `[kızgın]`, `[fısıltı]`, `[heyecanlı]` … metnin içinde etiket, o andan itibaren ses tonu değişir.
- 🎙️ **8 ses profili** — `erkek`, `derin_erkek`, `anlatici_erkek`, `kadin`, `yumusak_kadin`, `genc_erkek`, `robot`, `kaptan`.
- 🧹 **AI likini kıran insanileştirme** — mikro vibrato, yumuşak yüksek frekans tavanı, analog dithering.
- ⚡ **Akış (streaming)** — ilk ses parçası ~100 ms içinde.
- 🏃 **Eksiklik değil, ince ayar** — tek cümlede birden fazla duygu geçişi, parça aralarına doğal nefes payı.
- 💻 **Tamamen yerel** — CPU'da da çalışır, hiçbir veri dışarı çıkmaz.

## 🚀 Kurulum

```bash
pip install ema-lightning librosa soundfile scipy praat-parselmouth
```

Depoyu klonlayıp doğrudan kullanabilirsin:

```bash
git clone https://github.com/Syron01/frema-tts.git
cd frema-tts
pip install -e .
```

## 🎬 Hızlı Başlangıç

```python
from frema import Frema

f = Frema(voice="erkek")
f.say(
    "[mutlu] Merhaba! [ciddi] Bu bir test. [kızgın] Hızlan!",
    path="ornek.wav",
)
```

Tek satırda CLI:

```bash
python -m frema.cli "[romantik] Gecenin sessizliğinde yıldızlar parlıyordu." -v kadin -o gece.wav
python -m frema.cli --list            # sesler
python -m frema.cli --list-emotions   # duygular
```

## 🎭 Duygu Etiketleri

Metin içine köşeli parantezle yazılır; o noktadan itibaren geçerlidir, bir sonraki etiket gelene dek sürer.

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

İngilizce takma adlar da çalışır: `[angry]`, `[happy]`, `[whisper]`, `[sad]`, `[calm]` …

## 🎙️ Ses Profilleri

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

## 🌊 Canlı Akış (Düşük Gecikme)

```python
f = Frema(voice="anlatici_erkek")
for chunk in f.stream("[sakin] Merhaba, nasılsın?"):
    play(chunk)  # kendi oynatıcın
```

## ⏱️ Hız

```bash
python benchmark.py
```

Örnek ölçüm (CPU, RTX'siz dizüstü): RTF ~0.95 · ilk parça ~100 ms. GPU ile çok daha hızlı.

## 🔧 Nasıl Çalışır?

Frema, EMA Lightning'in 48 kHz mono çıktısını alıp üç katmandan geçirir:

1. **Prozodi hattı** — her duygu etiketi için per kaydırma (**PSOLA**, robot değil), kaset usulü tempo değişimi, kazanç, spektral eğim (parlaklık), vibrato ve tremolo.
2. **Ses profilleri** — formant (ses yolu) dönüşümü ile temel sesi erkek, derin, kadın, robot gibi karakterlere dönüştürür; ardından per ve EQ ince ayarı.
3. **İnsanileştirme** — mikro vibrato, tek yankı simulasyonu (room), dithering ve anlık drift ile "AI likini" maskeler.

## 📁 Proje Yapısı

```
frema/
├── core.py        # Frema sınıfı: say() / stream()
├── emotion.py     # duygu etiketleri ve prozodi tablosu
├── voices.py      # ses profilleri
├── processing.py  # pitch, tempo, EQ, vibrato, insanileştirme
└── cli.py         # komut satırı
examples/          # örnek .wav'ler
benchmark.py       # hız ölçümü
```

## ⚖️ Lisans

Apache-2.0. EMA Lightning ve normalizer-tr ile uyumludur. Ticari kullanıma uygundur.

> Orijinal model: https://huggingface.co/canberkkkkkk/ema-lightning
