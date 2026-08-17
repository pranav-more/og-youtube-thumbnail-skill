#!/usr/bin/env python3
"""Combine thumbnail candidates into a labeled comparison grid (A, B, C, D...)."""
import argparse
import string

from PIL import Image, ImageDraw, ImageFont

CELL_W, CELL_H, GAP = 640, 360, 8


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("-o", "--output", default="grid.png")
    args = ap.parse_args()

    n = len(args.images)
    cols = 2 if n > 1 else 1
    rows = (n + cols - 1) // cols
    grid = Image.new("RGB", (cols * CELL_W + (cols + 1) * GAP, rows * CELL_H + (rows + 1) * GAP), (12, 12, 14))

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except OSError:
        font = ImageFont.load_default()

    for i, path in enumerate(args.images):
        img = Image.open(path).convert("RGB").resize((CELL_W, CELL_H), Image.LANCZOS)
        d = ImageDraw.Draw(img)
        label = string.ascii_uppercase[i]
        d.rectangle([12, 12, 72, 68], fill=(0, 0, 0))
        d.text((30, 18), label, fill=(255, 255, 255), font=font)
        x = GAP + (i % cols) * (CELL_W + GAP)
        y = GAP + (i // cols) * (CELL_H + GAP)
        grid.paste(img, (x, y))

    grid.save(args.output)
    print(f"OK {args.output}")


if __name__ == "__main__":
    main()
