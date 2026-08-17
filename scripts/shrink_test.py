#!/usr/bin/env python3
"""Downscale candidates to 320x180 (the size that decides clicks) for the judge pass."""
import argparse
import os

from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("-o", "--outdir", default="small")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    for path in args.images:
        img = Image.open(path).convert("RGB")
        target = (320, 180) if img.width >= img.height else (180, 320)
        img.resize(target, Image.LANCZOS).save(
            os.path.join(args.outdir, os.path.basename(path))
        )
    print(f"OK {len(args.images)} images -> {args.outdir}/")


if __name__ == "__main__":
    main()
