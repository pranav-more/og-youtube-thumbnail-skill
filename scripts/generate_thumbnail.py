#!/usr/bin/env python3
"""Generate a YouTube thumbnail on fal.ai (Nano Banana family).

Usage:
  python3 generate_thumbnail.py --prompt "..." [--headshot face.jpg]
      [--reference img.png ...] [--examples ex1.jpg ...]
      [--model nb2|pro] [--aspect 16:9|9:16] [--output out.png]

Reference order sent to the model: headshot(s) first (Image 1), then references,
then style examples. With no input images, the text-to-image endpoint is used.
Requires: FAL_KEY env var; pip install requests pillow
"""
import argparse
import base64
import io
import mimetypes
import os
import sys
import time

import requests
from PIL import Image

MODELS = {
    "nb2": ("fal-ai/nano-banana-2", "fal-ai/nano-banana-2/edit"),
    "pro": ("fal-ai/nano-banana-pro", "fal-ai/nano-banana-pro/edit"),
}
QUEUE = "https://queue.fal.run"

EXAMPLES_SUFFIX = (
    "\n\nSTYLE EXAMPLES: The final attached images are thumbnails from high-performing "
    "YouTube videos on this topic. Study their composition, color usage, text placement, "
    "and visual hierarchy - then apply those patterns to create an ORIGINAL thumbnail. "
    "Do NOT copy these thumbnails. Use them as inspiration for what works."
)


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def validate_image(path: str) -> None:
    """Refuse HTML error pages and other non-images before they reach the model."""
    with open(path, "rb") as f:
        head = f.read(64)
    if head.lstrip()[:1] in (b"<", b"{"):
        die(f"{path} is not an image (looks like HTML/JSON — a failed download?)")
    try:
        Image.open(path).verify()
    except Exception as e:  # noqa: BLE001
        die(f"{path} failed image validation: {e}")


def to_data_uri(path: str, max_edge: int = 2048) -> str:
    validate_image(path)
    img = Image.open(path)
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        rgba = img.convert("RGBA")
        background.paste(rgba, mask=rgba.split()[-1])
        img = background
    else:
        img = img.convert("RGB")
    if max(img.size) > max_edge:
        img.thumbnail((max_edge, max_edge), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def fal_run(model: str, payload: dict, key: str, timeout_s: int = 240) -> dict:
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    r = requests.post(f"{QUEUE}/{model}", json=payload, headers=headers, timeout=60)
    if r.status_code >= 400:
        die(f"fal submit {model}: {r.status_code} {r.text[:300]}")
    req = r.json()
    status_url = req.get("status_url") or f"{QUEUE}/{model}/requests/{req['request_id']}/status"
    result_url = req.get("response_url") or f"{QUEUE}/{model}/requests/{req['request_id']}"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        s = requests.get(status_url, headers=headers, timeout=30).json()
        if s.get("status") == "COMPLETED":
            return requests.get(result_url, headers=headers, timeout=60).json()
        if s.get("status") in ("FAILED", "ERROR"):
            die(f"fal generation failed: {s}")
        time.sleep(2)
    die("fal generation timed out")
    return {}  # unreachable


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--headshot", action="append", default=[])
    ap.add_argument("--reference", action="append", default=[])
    ap.add_argument("--examples", action="append", default=[])
    ap.add_argument("--model", choices=list(MODELS), default="nb2")
    ap.add_argument("--aspect", choices=["16:9", "9:16"], default="16:9")
    ap.add_argument("--resolution", choices=["0.5K", "1K", "2K"], default="1K")
    ap.add_argument("--output", default="thumbnail.png")
    ap.add_argument("--no-style", action="store_true", help="skip brand-style.md")
    args = ap.parse_args()

    key = os.environ.get("FAL_KEY")
    if not key:
        die("FAL_KEY is not set")

    prompt = args.prompt
    style_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand-style.md")
    if not args.no_style and os.path.exists(style_path):
        with open(style_path, encoding="utf-8") as f:
            style = f.read().strip()
        if style:
            prompt += "\n\nBRAND STYLE GUIDE (follow these rules):\n" + style
    if args.examples:
        prompt += EXAMPLES_SUFFIX

    images = [to_data_uri(p) for p in (args.headshot + args.reference + args.examples)]
    t2i, edit = MODELS[args.model]
    model = edit if images else t2i
    payload: dict = {
        "prompt": prompt,
        "aspect_ratio": args.aspect,
        "resolution": args.resolution,
        "num_images": 1,
        "output_format": "png",
    }
    if images:
        payload["image_urls"] = images

    t0 = time.time()
    result = fal_run(model, payload, key)
    imgs = result.get("images") or []
    if not imgs:
        die(f"no images in response: {str(result)[:300]}")

    raw = requests.get(imgs[0]["url"], timeout=120).content
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    target = (1280, 720) if args.aspect == "16:9" else (720, 1280)
    # cover-crop to exact target
    scale = max(target[0] / img.width, target[1] / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (img.width - target[0]) // 2
    top = (img.height - target[1]) // 2
    img = img.crop((left, top, left + target[0], top + target[1]))
    img.save(args.output)
    if not os.path.exists(args.output):
        die("output file was not written")
    print(f"OK {args.output} ({model}, {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
