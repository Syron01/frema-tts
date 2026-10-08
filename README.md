# Frema ⚡

**Frema**, insandan ayırt edilemeyen, sıfır robotiklik ve sıfır cızırtı hedefiyle tasarlanmış, **tok ve net** ses kalitesine sahip yeni nesil Türkçe yapay zekâ ses motorudur. Doğrudan stüdyo kalitesinde **.mp3** formatında çıktı üretir. Tamamen yerel (offline) çalışır, API anahtarı istemez.

[![Lisans](https://img.shields.io/badge/lisans-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Motor](https://img.shields.io/badge/motor-Trendyol--TTS%202.38B%20%7C%20EMA--TTS%2065M-green)](https://huggingface.co/Trendyol/Trendyol-TTS)

---

## 🎧 Neden Frema? (Robotik Seslere Son)

Standart TTS sistemlerinde sıkça karşılaşılan şu kronik sorunlar Frema'da tamamen çözülmüştür:

1. **Sıfır Kesilme (Akustik Sınır Koruması / Envelope Guard):** Cümle başlarken ilk harf (`b`, `p`, `t`, `k`), cümle biterken ise son karakter asla havada kalmaz veya kırpılmaz. Konuşma öncesi ve sonrasına eklenen temiz akustik tampon sayesinde cümlenin tamamı eksiksiz ve pürüzsüz telaffuz edilir.
2. **Tok ve Net Ses (Stüdyo Mastering EQ):** Yapay vibrato, faz vokoderi ve beyaz gürültü tamamen kaldırılmıştır. Bunun yerine 140 Hz göğüs dolgunluğu ("tokluk") ve 3.2 kHz berraklık ("netlik") sunan minimum-faz parametrik stüdyo ekolayzırı uygulanır.
3. **İnsansı Doğallık:** 2.38 milyar parametreli VoxCPM2 Türkçe mimarisi (UTMOS 3.83) ile insan konuşmacıdan farksız akıcılık ve nefes temposu.
4. **Doğrudan .mp3 Çıktısı:** Yüksek bant genişliğinde 48 kHz stereo MP3 formatında anında paylaşıma ve dinlemeye hazır ihracat.

---

## ✨ Motor Seçenekleri

| Motor | Parametre | Ses Karakteri | Kullanım Amacı |
|---|---|---|---|
| `trendyol` *(Varsayılan)* | 2.38B | Çok tok, derin, insanla birebir, sıfır robotiklik | Podcast, dublaj, sesli kitap, üst düzey yayın |
| `ematts` | 65M | Hızlı, akıcı, hız kontrolü yapılmış, hafif | Gerçek zamanlı asistan, anlık canlı akış (streaming) |

---

## 🚀 Kurulum

```bash
pip install torch soundfile scipy pyloudnorm voxcpm librosa
pip install -e .
```

---

## 🎬 Hızlı Başlangıç

### Python API

```python
from frema import Frema

# 1. En doğal, tok ve insansı ses (Varsayılan: Trendyol 2.38B)
f = Frema(engine="trendyol", voice="tok_erkek")
f.say(
    "[ciddi] Sayın dinleyiciler, hoş geldiniz. [sakin] Bugün yapay zekanın ulaştığı en berrak ses kalitesini dinliyorsunuz.",
    path="yayin.mp3"
)

# 2. Hızlı motor seçeneği (EMA-TTS 65M)
f_fast = Frema(engine="ematts", voice="podcast", speed=0.9)
f_fast.say("Hızlı ve hafif motorla üretilen net stüdyo kaydı.", path="hizli.mp3")
```

### Komut Satırı (CLI)

```bash
# Varsayılan motor ile doğrudan .mp3 üretimi
python -m frema.cli "[ciddi] Başlarken de duyduğunuz gibi sesimiz artık son derece tok ve net." -o cikti.mp3

# Farklı ses profili ve hız seçeneği
python -m frema.cli "Gecenin sessizliğinde yıldızlar parlıyordu." -v podcast -s 0.92 -o podcast.mp3

# Hızlı motor ile üretim
python -m frema.cli "Anlık hızlı ses üretimi." --engine ematts -o hizli.mp3

# Seçenekleri listeleme
python -m frema.cli --list
python -m frema.cli --list-emotions
```

---

## 🎙️ Ses Profilleri

- `tok_erkek` / `varsayilan`: Derin göğüs rezonanslı, zengin ve sıcak erkek spiker sesi.
- `derin_anlatici`: Ağırbaşlı, sakin, belgesel ve sinematik anlatıcı tonu.
- `podcast`: Samimi, yakın mikrofonlu, sıcak ve akıcı podcast ses tonu.
- `haber_spikeri`: Berrak, öne çıkan, diksiyonu keskin bülten sunucusu tonu.
- `kadin`: Net ve temiz kadın profili.
- `yumusak`: Dinlendirici, ılık ve yumuşak tonlama.

---

## 🎭 Duygu Etiketleri

Metin içine `[etiket]` şeklinde eklenir:
- `[sakin]`: Dingin tempo, ölçülü tonlama.
- `[ciddi]`: Tok gövde, otoriter ve net tonlama.
- `[anlatıcı]`: Akıcı hikâye ritmi, zengin rezonans.
- `[güçlü]`: Enerjik, vurgulu ve kendinden emin.
- `[haber]`: Spiker ritmi ve öne çıkan diksiyon.
- `[mutlu]`: Canlı ve aydınlık tını.

---

## 📁 Proje Yapısı

```
frema/
├── core.py        # Frema ana sentez sınıfı: Trendyol & EMA motorları
├── processing.py  # Stüdyo DSP: Tok/net EQ, zarf koruması, -16 LUFS limiter, MP3
├── voices.py      # Ses profilleri ve EQ haritaları
├── emotion.py     # Duygu etiketleri ve doğal tempo dinamikleri
└── cli.py         # Komut satırı arayüzü (.mp3 varsayılan)
test/
├── test_insansi_tok_net.mp3   # Amiral gemisi referans stüdyo testi
└── test_ematts_hizli.mp3      # Hızlı motor stüdyo testi
tests/
└── test_core.py   # Birim testleri
```

## ⚖️ Lisans

Apache-2.0. Ticari ve kişisel kullanıma uygundur.
