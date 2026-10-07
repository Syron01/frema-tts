from voxcpm import VoxCPM
import soundfile as sf, numpy as np

m = VoxCPM.from_pretrained('Trendyol/Trendyol-TTS', load_denoiser=False, optimize=True)
text = (
    "Hoş geldiniz... bu gece anlatacağım hikâye kolay dinlenmez. "
    "Siz buradayken, şehir susmuş; sokak lambaları titreyip sönüyor. "
    "Sanki bir şey arkanızdaymış gibi... donüp dönüp bakıyorsunuz. "
    "O an... hepimiz biliyoruz: yalnız değiliz. "
    "Ama kimsenin çıkıp söylemediği bir gerçek var. "
)
text = (text + " ") * 6
wav = m.generate(text, cfg_value=2.0, inference_timesteps=32, normalize=True)
sr = 48000
wav = np.asarray(wav, dtype=np.float32)
sf.write('test/trendyol_podcast.wav', wav, sr, subtype='PCM_24')
print('sn:', len(wav)/sr)
