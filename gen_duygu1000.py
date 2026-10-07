import sys
sys.path.insert(0, 'ema-tts')
import torch, soundfile as sf
import numpy as np
from inference import EmaTTS

device = 'cuda'
tts = EmaTTS.from_pretrained('ema-tts/ckpt', device=device)
text = ("Durun... istediğinizi anlatayım. Bugün gerçekten çok özel bir şey paylaşacağım sizinle. "
        "Biliyorsunuz, aylardır beklediğimiz proje... sonunda tamamlandı. İnanılır gibi değil! "
        "İlk kez bu kadar gurur duydum. Şimdi birlikte dinliyoruz.")
wav = tts.say(text, steps=1000, seed=7)
sr = tts.sample_rate
stereo = np.stack([wav, wav], axis=-1)
sf.write('test/duygu_1000.wav', stereo, sr, subtype='PCM_24')
print('sn:', len(wav)/sr)
