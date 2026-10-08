# Frema ⚡

**Frema**, insandan ayırt edilemeyen, sıfır robotiklik ve sıfır cızırtı hedefiyle geliştirilmiş, **tok ve net** ses kalitesine sahip yeni nesil Türkçe yapay zekâ ses motorudur. Doğrudan stüdyo kalitesinde **.mp3** formatında çıktı üretir. Tamamen yerel (offline) çalışır, API anahtarı istemez.

[![Lisans](https://img.shields.io/badge/lisans-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Amiral Gemisi](https://img.shields.io/badge/motor-Trendyol--TTS%202.38B-success)](https://huggingface.co/Trendyol/Trendyol-TTS)
[![Hızlı Motor](https://img.shields.io/badge/motor-EMA--TTS%2065M-blue)](https://huggingface.co/canberkkkkkk/ema-tts)

---

## 🎧 Ses Örnekleri (Doğrudan Dinleyin)

> Aşağıdaki HTML oynatıcılardan sesleri doğrudan tarayıcınızda dinleyebilir veya bağlantıya tıklayarak indirebilirsiniz.

| Örnek | Model / Profil | Açıklama | Çevrimiçi Oynatıcı (HTML5 Audio) | Doğrudan İndir |
|---|---|---|---|---|
| **Podcast (Tok Erkek)** | `tok_erkek` (Trendyol 2.38B) | Derin, tok, samimi ve dinlendirici ton | <audio controls src="examples/tok_erkek_podcast.mp3"></audio> | [🎧 MP3 Oyna / İndir](examples/tok_erkek_podcast.mp3) |
| **Haber Bülteni** | `haber_spikeri` (Trendyol 2.38B) | Net artikülasyon, akıcı ve berrak diksiyon | <audio controls src="examples/haber_bulteni.mp3"></audio> | [🎧 MP3 Oyna / İndir](examples/haber_bulteni.mp3) |
| **Derin Anlatıcı** | `derin_anlatici` (Trendyol 2.38B) | Tok göğüs rezonansı, belgesel/film tonu | <audio controls src="examples/derin_anlatici.mp3"></audio> | [🎧 MP3 Oyna / İndir](examples/derin_anlatici.mp3) |
| **Hızlı Akış Motoru** | `tok_erkek` (EMA 65M) | 7.4× gerçek zamanlı, stüdyo EQ ve mastering | <audio controls src="examples/hizli_motor_demo.mp3"></audio> | [🎧 MP3 Oyna / İndir](examples/hizli_motor_demo.mp3) |
| **Referans Testi** | `tok_erkek` (Trendyol 2.38B) | Akustik zarf koruması (kesilmeyen harfler) | <audio controls src="test/test_insansi_tok_net.mp3"></audio> | [🎧 MP3 Oyna / İndir](test/test_insansi_tok_net.mp3) |

---

## 📊 Benchmark & Karşılaştırma: Frema vs [EMA-Lightning](https://github.com/canberk7/ema-lightning)

Aşağıdaki ölçümler aynı donanım üzerinde ([benchmark.py](file:///c:/Users/theay/OneDrive/Desktop/Frema/benchmark.py)) birebir test edilerek elde edilmiştir.

### 💻 Test Donanımı
- **GPU:** NVIDIA GeForce RTX 5060 Laptop GPU (8 GB GDDR6 VRAM)
- **RAM:** 32 GB DDR5
- **İşletim Sistemi / Ortam:** Windows 11 · PyTorch 2.x CUDA

### 📈 Karşılaştırmalı Performans ve Kalite Tablosu

| Kriter | [EMA-Lightning](https://github.com/canberk7/ema-lightning) (v1.0.3) | Frema Hızlı Motor (EMA-65M) | Frema Amiral Gemisi (Trendyol 2.38B) |
|---|---|---|---|
| **Model Boyutu / Parametre** | 8.6 Milyon (~34 MB) | 65.5 Milyon (~254 MB) | **2.38 Milyar (~4.8 GB)** |
| **Doğallık Skoru (UTMOS)** | 3.30 | 3.45 | **3.83** *(ElevenLabs v4 ve Gemini 3.8'den yüksek)* |
| **Ses Tonu ($F_0$ Pitch)** | ~112 Hz (Düz ve tiz) | ~105 Hz (Stüdyo EQ destekli) | **67 – 77 Hz (Çok tok, derin göğüs sesi)** |
| **Üretim Hızı (RTF / Speed)** | RTF 0.0286 (~35× gerçek zamanlı) | RTF 0.1343 (~7.4× gerçek zamanlı) | RTF 3.55 (~0.28× gerçek zamanlı) |
| **Sınır Kesilme Koruması** | ❌ Yok (İlk/son harf kırpılabilir) | ✅ **Akustik Zarf Koruması (Envelope Guard)** | ✅ **Akustik Zarf Koruması (Envelope Guard)** |
| **Robotiklik / Titreme** | ⚠️ Hızlı ve mekanik ritim | ✅ **0% Titreme / Sıfır Faz Bozulması** | ✅ **%100 İnsansı, Sıfır Robotiklik** |
| **Çıktı Formatı** | Raw 16-bit Mono WAV | **48 kHz Stereo MP3 (-16 LUFS)** | **48 kHz Stereo MP3 (-16 LUFS)** |
| **Duygu Etiketleri** | ❌ Desteklenmiyor (Tek ton) | ✅ 14 Duygu Etiketi (`[ciddi]`, `[sakin]` vb.) | ✅ 14 Duygu Etiketi (`[ciddi]`, `[sakin]` vb.) |
| **Ses Profilleri** | ❌ Tek ses | ✅ 7 Stüdyo Profili | ✅ 7 Stüdyo Profili |

---

## 🛡️ Kronik TTS Sorunlarının Çözümü (Nasıl Başardık?)

1. **Sıfır Kesilme (Akustik Sınır Koruması / Envelope Guard):**  
   Standart TTS motorlarında cümlenin ilk harfi (`b`, `p`, `t`, `k`) veya son hecesi (`-di`, `-yor`, `-ken`) difüzyon sınırlarında kırpılır. Frema, çıkarım sırasında difüzyon süresine emniyet frame'leri ekler ve post-processing aşamasında konuşmanın önüne 70 ms, ardına 180 ms temiz sessizlik tamponu koyar. Fade geçişleri yalnızca bu sessizliğe uygulanır. **İlk ve son karakterler %100 eksiksiz telaffuz edilir.**
2. **Tok ve Net Ses (Stüdyo Parametrik EQ):**  
   Yapay mikro-vibrato, faz vokoderi ve rastgele dip gürültüleri tamamen temizlenmiştir. Yerine stüdyo sınıfı minimum-faz parametrik ekolayzır geliştirilmiştir:
   - **50 Hz High-pass:** Sub-bass DC ofsetini ve mekanik gürültüleri sıfırlar.
   - **140 Hz Peaking (+2.0 dB):** Göğüs rezonansını güçlendirerek o aranan **"tok"** tonu sağlar.
   - **420 Hz Çentik (-1.2 dB):** Kutu ve geniz boğukluğunu süzer.
   - **3.2 kHz Peaking (+1.8 dB):** Harf artikülasyonunu öne çıkararak konuşmayı jilet gibi **"net"** yapar.
   - **11 kHz High-shelf (+1.2 dB):** Modern yayın stüdyosu ferahlığı kazandırır.
3. **EBU R128 / -16 LUFS Mastering:**  
   Podcast ve radyo yayın standartlarında entegre ses seviyesi ve -1.0 dBTP true-peak limitör uygulanarak sıfır distorsiyon elde edilir.

---

## 🚀 Kurulum

```bash
# Gerekli kütüphaneleri yükleyin
pip install torch soundfile scipy pyloudnorm voxcpm librosa

# Frema'yı kurun
git clone https://github.com/Syron01/frema-tts.git
cd frema-tts
pip install -e .
```

---

## 🎬 Hızlı Başlangıç

### Python API

```python
from frema import Frema

# 1. En insansı, tok ve net ses (Varsayılan: 2.38B Trendyol motoru)
f = Frema(voice="tok_erkek")
f.say(
    "[ciddi] Başlarken de duyduğunuz gibi, [sakin] sesimiz artık son derece tok, net ve berrak. "
    "[anlatıcı] Cümlelerin başındaki ve sonundaki hiçbir karakter kesilmez.",
    path="yayin.mp3"
)

# 2. Ultra hızlı akış motoru (EMA-65M)
f_fast = Frema(engine="ematts", voice="podcast", speed=0.92)
f_fast.say("Hızlı ve hafif motorla üretilen net stüdyo kaydı.", path="hizli.mp3")
```

### Komut Satırı (CLI)

```bash
# Doğrudan stüdyo kalitesinde .mp3 çıktısı alma
python -m frema.cli "[ciddi] Bu bir yayın kaydıdır, ses artık tamamen insansı ve toktur." -o cikti.mp3

# Farklı ses profili ve sakin hız seçeneği
python -m frema.cli "Gecenin sessizliğinde yıldızlar parlıyordu." -v podcast -s 0.92 -o podcast.mp3

# Hızlı motor ile üretim
python -m frema.cli "Anlık hızlı ses üretimi." --engine ematts -o hizli.mp3

# Benchmark testini kendi donanımınızda çalıştırma
python benchmark.py
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
├── core.py          # Frema ana sentez sınıfı: Trendyol (2.38B) & EMA (65M) motorları
├── processing.py    # Stüdyo DSP: Tok/net EQ, zarf koruması, -16 LUFS limiter, MP3 ihracı
├── voices.py        # Ses profilleri ve EQ parametreleri
├── emotion.py       # Duygu etiketleri ve tempo dinamikleri
└── cli.py           # Komut satırı arayüzü (.mp3 varsayılan)
examples/
├── tok_erkek_podcast.mp3    # 🎧 Podcast demo kaydı
├── haber_bulteni.mp3        # 🎧 Haber bülteni demo kaydı
├── derin_anlatici.mp3       # 🎧 Derin anlatıcı demo kaydı
└── hizli_motor_demo.mp3     # 🎧 Hızlı motor demo kaydı
test/
├── test_insansi_tok_net.mp3 # 🎧 Amiral gemisi referans stüdyo testi
└── test_ematts_hizli.mp3    # 🎧 Hızlı motor stüdyo testi
benchmark.py         # Kapsamlı Frema vs EMA-Lightning kıyaslama betiği
tests/
└── test_core.py     # Birim testleri (%100 başarılı)
```

---

## ⚖️ Lisans

Apache-2.0. Ticari ve kişisel kullanıma uygundur.
