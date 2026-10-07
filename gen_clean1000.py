import sys
sys.path.insert(0, 'ema-tts')
import torch, soundfile as sf
import numpy as np
from inference import EmaTTS

device = 'cuda'
tts = EmaTTS.from_pretrained('ema-tts/ckpt', device=device)
text = ("Az önce ajanslara düşen bilgilere göre, ülke genelinde etkili olacak kar yağışının "
        "üç gün süreceği tahmin ediliyor. Meteoroloji uzmanları, özellikle yüksek kesimlerde "
        "buzlanma ve ulaşımda aksamalar yaşanabileceği konusunda uyarıda bulundu. Yetkililer, "
        "sürücülerin zorunlu olmadıkça trafiğe çıkmamasını istedi.")
wav = tts.say(text, steps=1000, seed=0)
sr = tts.sample_rate
stereo = np.stack([wav, wav], axis=-1)
sf.write('test/temiz_1000.wav', stereo, sr, subtype='PCM_24')
print('sn:', len(wav)/sr)
