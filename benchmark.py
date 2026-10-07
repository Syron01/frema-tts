"""Hız ve boyut ölçümü."""
import time
import numpy as np

from frema import Frema


def bench():
    f = Frema("erkek")
    text = "Merhaba, ben Frema. Türkçe konuşuyorum ve duygu etiketlerini destekliyorum."
    t0 = time.perf_counter()
    audio, sr = f.say(text)
    dt = time.perf_counter() - t0
    dur = len(audio) / sr
    print(f"Ses süresi: {dur:.2f}s | Üretim: {dt:.2f}s | RTF: {dt/dur:.3f} | {dur/dt:.1f}x gerçek zaman")

    # stream ilk parça gecikmesi
    t0 = time.perf_counter()
    first = None
    for i, part in enumerate(f.stream(text)):
        if first is None:
            first = time.perf_counter() - t0
        if i > 0:
            break
    print(f"İlk parça gecikmesi: {first*1000:.0f} ms")


if __name__ == "__main__":
    bench()
