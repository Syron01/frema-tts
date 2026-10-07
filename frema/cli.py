"""Frema komut satırı."""
import argparse
import sys

from .core import Frema
from .voices import VOICES
from .emotion import EMOTIONS


def main():
    p = argparse.ArgumentParser(prog="frema", description="Frema TTS - Türkçe duygu kontrollü ses")
    p.add_argument("text", nargs="*", help="Okunacak metin (etiketli olabilir)")
    p.add_argument("-o", "--out", default="cikti.wav")
    p.add_argument("-v", "--voice", default="erkek", choices=list(VOICES))
    p.add_argument("-s", "--speed", type=float, default=1.0)
    p.add_argument("--list", action="store_true", help="Sesleri listele")
    p.add_argument("--list-emotions", action="store_true")
    args = p.parse_args()
    if args.list:
        print("Sesler:", ", ".join(VOICES))
        return
    if args.list_emotions:
        print("Duygular:", ", ".join(EMOTIONS))
        return
    text = " ".join(args.text) if args.text else sys.stdin.read()
    f = Frema(args.voice, speed=args.speed)
    f.say(text, path=args.out)
    print("Yazıldı:", args.out)


if __name__ == "__main__":
    main()
