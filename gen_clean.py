import sys
sys.path.insert(0, 'ema-tts')
import torch, soundfile as sf
from inference import EmaTTS

device = 'cuda'
tts = EmaTTS.from_pretrained('ema-tts/ckpt', device=device)
text = ("Az önce ajanslara düşen bilgilere göre, ülke genelinde etkili olacak kar yağışının "
        "üç gün süreceği tahmin ediliyor. Meteoroloji uzmanları, özellikle yüksek kesimlerde "
        "buzlanma ve ulaşımda aksamalar yaşanabileceği konusunda uyarıda bulundu. Yetkililer, "
        "sürücülerin zorunlu olmadıkça trafiğe çıkmamasını istedi.")
wav = tts.say(text, steps=64, seed=0)
sr = tts.sample_rate
# Faz güvenli stereo: aynı sesin iki kanalını birebir, hafif derinlik için sağa -24dB 20ms gecikmeli kopya ekle
import numpy as np
left = wav
right = np.roll(wav, int(sr*0.02)) * 0.92
right[:int(sr*0.02)] = 0
stereo = np.stack([left, right], axis=-1)
sf.write('test/temiz_kadin.wav', stereo, sr, subtype='PCM_24')
print('bövlüm:', len(wav)/sr, 'sn ->', 'test/temiz_kadin.wav')
