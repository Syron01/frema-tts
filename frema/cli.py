"""Frema komut satırı: Tok, net ve doğal Türkçe AI ses sistemi."""

from __future__ import annotations

import argparse
import sys

from .core import Frema
from .voices import VOICES
from .emotion import EMOTIONS


def main():
    p = argparse.ArgumentParser(
        prog="frema",
        description="Frema - En doğal, tok ve net Türkçe yapay zekâ ses motoru (.mp3 çıktısı)",
    )
    p.add_argument("text", nargs="*", help="Okunacak metin (isteğe bağlı [ciddi], [sakin] vb. etiketli)")
    p.add_argument("-o", "--out", default="cikti.mp3", help="Çıktı ses dosyası yolu (varsayılan: cikti.mp3)")
    p.add_argument("-v", "--voice", default="varsayilan", choices=list(VOICES), help="Ses profili")
    p.add_argument("-s", "--speed", type=float, default=1.0, help="Konuşma hızı çarpanı (örn: 0.9 = daha sakin ve tok)")
    p.add_argument(
        "--engine",
        default="trendyol",
        choices=["trendyol", "ematts"],
        help="Ses motoru: 'trendyol' (en insansı 2.38B) veya 'ematts' (hafif 65M)",
    )
    p.add_argument("--steps", type=int, default=None, help="Çıkarım adım sayısı")
    p.add_argument("--seed", type=int, default=None, help="Rastgelelik çekirdeği")
    p.add_argument("--list", action="store_true", help="Ses profillerini listele")
    p.add_argument("--list-emotions", action="store_true", help="Duygu etiketlerini listele")
    args = p.parse_args()

    if args.list:
        print("Mevcut Ses Profilleri:")
        for name in VOICES:
            print(f"  - {name}")
        return

    if args.list_emotions:
        print("Mevcut Duygu Etiketleri:")
        for name in EMOTIONS:
            print(f"  - [{name}]")
        return

    text = " ".join(args.text).strip() if args.text else sys.stdin.read().strip()
    if not text:
        print("Hata: Okunacak metin belirtilmedi.", file=sys.stderr)
        p.print_help()
        sys.exit(1)

    # Dosya uzantısını garantiye al (mp3)
    out_path = args.out
    if not (out_path.lower().endswith(".mp3") or out_path.lower().endswith(".wav")):
        out_path = out_path + ".mp3"

    print(f"Ses üretiliyor... [Motor: {args.engine}, Profil: {args.voice}, Hız: {args.speed}]")
    f = Frema(voice=args.voice, speed=args.speed, engine=args.engine)
    f.say(text, path=out_path, seed=args.seed, steps=args.steps)
    print(f"İşlem tamamlandı. Dosya kaydedildi: {out_path}")


if __name__ == "__main__":
    main()
