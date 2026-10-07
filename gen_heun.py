import sys, math
sys.path.insert(0, 'ema-tts')
import torch, numpy as np, soundfile as sf
from inference import EmaTTS, _codec, _find
from model import prepare_text
from text import prepare
json = __import__('json')

device = 'cuda'
root = 'ema-tts/ckpt'
cfg = json.load(open(_find(root, 'config.json'), encoding='utf-8'))
from model import EmaTTS as _Net, Vocab
vocab = Vocab.from_list(cfg['vocab'])
net = _Net(len(vocab.itos), latent_dim=cfg['latent_dim'], d=cfg['d_model'], n_layers=cfg['n_layers'], n_heads=cfg['n_heads'], text_conv=cfg['text_conv'], align_heads=cfg['align_heads'], pos_scale=cfg['pos_scale'], lookback=cfg['lookback'], lookahead=cfg['lookahead'], dur_hidden=cfg['dur_hidden']).to(device)
from safetensors.torch import load_file
net.load_state_dict(load_file(_find(root, 'model.safetensors')), strict=True)
net.eval()
vae = _codec(cfg, device)
ema = EmaTTS(net, vocab, vae, cfg, device)

@torch.no_grad()
def generate_heun(tts, text, steps=512, seed=0):
    if seed is not None: torch.manual_seed(seed)
    ids, spans = prepare_text(prepare(text, lead=cfg['lead']), vocab, device)
    # mimic Net.generate but Heun
    dev = ids.device
    tmask = ids != 0
    h = net.text(ids)
    L = ids.shape[1]
    char_word = torch.full((1, L), -1, dtype=torch.long, device=dev)
    char_pos = torch.zeros(1, L, device=dev)
    for w, (a, b) in enumerate(spans):
        n = b - a
        for j in range(n):
            char_word[0, a + j] = w
            char_pos[0, a + j] = (j + 0.5) / n
    _, contrib = net.chardur(h, tmask)
    d = torch.zeros(len(spans), device=dev)
    for w, (a, b) in enumerate(spans):
        d[w] = contrib[0, a:b].sum()
    d = d.round().long().clamp(min=0, max=250)
    for w, (a, b) in enumerate(spans):
        if b > a and d[w] < 1: d[w] = 1
    T = min(int(d.sum().item()), 3000)
    frame_word = torch.zeros(1, T, dtype=torch.long, device=dev)
    frame_pos = torch.zeros(1, T, device=dev)
    f = 0
    for w in range(len(spans)):
        n = int(d[w])
        for j in range(n):
            if f >= T: break
            frame_word[0, f] = w
            frame_pos[0, f] = (j + 0.5) / max(1, n)
            f += 1
    cond, _ = net.aligner(h, char_word, char_pos, frame_word, frame_pos, tmask)
    fmask = torch.ones(1, T, dtype=torch.bool, device=dev)
    x = torch.randn(1, T, net.latent_dim, device=dev)
    dt = 1.0 / steps
    for i in range(steps):
        t = torch.full((1,), i * dt, device=dev)
        k1 = net.backbone(x, cond, t, fmask)
        t2 = torch.full((1,), (i + 1) * dt, device=dev)
        k2 = net.backbone(x + dt * k1, cond, t2, fmask)
        x = x + dt * (k1 + k2) / 2
    lat = x
    wav = vae.decode(lat.transpose(1, 2)).squeeze()
    wav = np.clip(wav.float().cpu().numpy(), -1, 1)
    return ema.master(wav)

text = ("Dinle... kimse burada olduğunu bilmesin. "
        "Odama girdiğimde, ışıklar henüz sönmemişti... ama bir şeyler değişmişti. "
        "Köşedeki pencereden içeri vuran ay ışığı, duvardaki gölgeleri garip bir şekilde uzatmıştı. "
        "Arkamdan gelen adım sesini duydum... soğuktu. "
        "O an anladım ki, yalnız değilim.")
wav = generate_heun(ema, text, steps=512, seed=3)
sr = ema.sample_rate
stereo = np.stack([wav, wav], axis=-1)
sf.write('test/creepy_hq.wav', stereo, sr, subtype='PCM_24')
print('sn:', len(wav)/sr)
