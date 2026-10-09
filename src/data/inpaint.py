"""Overlay removal for the Phase 3 mitigation.

Detected text boxes (OCR) and orange redaction boxes are slightly dilated and
filled with OpenCV Telea inpainting. Inpainting is used instead of a solid fill
because a uniform gray rectangle would itself become a visible marker of
"this image had an overlay", which is the shortcut we are trying to remove.
Undetected overlays (small corner logos, stylized captions) are not removed.
"""
import json
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def _n_letters(text: str) -> int:
    return len(re.findall(r"[^\W\d_]", text))


def keep_text_box(d: dict, min_conf: float, min_chars: int, low_conf: float, low_min_letters: int) -> bool:
    """Phase 1 rule (confident, >= min_chars) or a lower-confidence box with real
    letters. The low tier was added after visual review: it recovers Russian
    captions read at confidence 0.29 to 0.44, and all 11 images it adds were
    confirmed to be genuine overlay text."""
    if d["conf"] >= min_conf and len(d["text"].strip()) >= min_chars:
        return True
    return d["conf"] >= low_conf and _n_letters(d["text"]) >= low_min_letters


def overlay_boxes(ocr_json: Path, orange_json: Path, min_conf: float = 0.5, min_chars: int = 2,
                  low_conf: float = 0.25, low_min_letters: int = 3) -> dict[str, list]:
    ocr = json.loads(Path(ocr_json).read_text(encoding="utf-8"))
    orange = json.loads(Path(orange_json).read_text(encoding="utf-8"))
    out = {}
    for name in ocr:
        boxes = [d["bbox"] for d in ocr[name] if keep_text_box(d, min_conf, min_chars, low_conf, low_min_letters)]
        out[name] = boxes + orange.get(name, [])
    return out


def inpaint_image(im: Image.Image, boxes, dilate_frac: float = 0.3, min_pad: int = 3, radius: int = 5) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    if not boxes:
        return im
    arr = np.asarray(im).copy()
    h, w = arr.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    for x0, y0, x1, y1 in boxes:
        pad = max(min_pad, int(dilate_frac * (y1 - y0)))
        mask[max(0, int(y0) - pad):min(h, int(y1) + pad), max(0, int(x0) - pad):min(w, int(x1) + pad)] = 255
    return Image.fromarray(cv2.inpaint(arr, mask, radius, cv2.INPAINT_TELEA))
