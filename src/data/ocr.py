"""Text and watermark detection with easyocr.

Boxes are stored in original-image pixel coordinates so Phase 3 can measure how
much Grad-CAM mass falls on text regions.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

MAX_SIDE = 1280  # downscale very large images for speed, boxes are rescaled back


def ocr_image(reader, im: Image.Image) -> list[dict]:
    """Detections for one RGB image (already EXIF-transposed), boxes in its pixels.
    Shared by the offline audit and the inference pipeline."""
    scale = min(1.0, MAX_SIDE / max(im.size))
    if scale < 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BILINEAR)
    dets = []
    for box, text, conf in reader.readtext(np.asarray(im)):
        box = np.asarray(box, dtype=float) / scale
        x0, y0 = box.min(axis=0)
        x1, y1 = box.max(axis=0)
        dets.append({"text": text, "conf": float(conf), "bbox": [float(x0), float(y0), float(x1), float(y1)]})
    return dets


def run_ocr(paths: list[Path], langs=("ch_sim", "en"), gpu: bool = True) -> list[list[dict]]:
    import easyocr

    reader = easyocr.Reader(list(langs), gpu=gpu, verbose=False)
    out = []
    for p in paths:
        with Image.open(p) as im:
            out.append(ocr_image(reader, ImageOps.exif_transpose(im).convert("RGB")))
    return out


def text_area_fraction(dets: list[dict], width: int, height: int, min_conf: float) -> float:
    """Fraction of image pixels covered by the union of confident text boxes."""
    mask = np.zeros((height, width), dtype=bool)
    for d in dets:
        if d["conf"] < min_conf:
            continue
        x0, y0, x1, y1 = (int(round(v)) for v in d["bbox"])
        mask[max(0, y0):min(height, y1), max(0, x0):min(width, x1)] = True
    return float(mask.mean())


def merge_passes(passes: list[list[list[dict]]]) -> list[list[dict]]:
    """Concatenate detections from several language passes (easyocr cannot load
    ch_sim and ru in one reader). Overlapping boxes are kept, area is computed on
    the union mask so duplicates do not inflate it."""
    return [sum(per_image, []) for per_image in zip(*passes)]


def orange_redaction_boxes(path: Path, min_area_frac: float = 0.015, max_area_frac: float = 0.06,
                           min_aspect: float = 2.5, max_aspect: float = 4.5) -> list[list[float]]:
    """Detect the solid orange rectangles (with pixelated text inside) that appear
    on many images. Returns bboxes of orange connected components that are
    roughly rectangular (fill ratio of the bounding box above 0.6).

    The size and aspect limits match the overlay's fixed shape (about 3.3% of the
    image, aspect about 2.9). They were added in Phase 3 after a review of every
    detection: without them the detector also fired on a wooden floor, an orange
    blanket, a cloth edge, a floor patch and a region of skin (5 of 37 images)."""
    with Image.open(path) as im:
        return orange_boxes_in_image(ImageOps.exif_transpose(im).convert("RGB"), min_area_frac, max_area_frac,
                                     min_aspect, max_aspect)


def orange_boxes_in_image(im: Image.Image, min_area_frac: float = 0.015, max_area_frac: float = 0.06,
                          min_aspect: float = 2.5, max_aspect: float = 4.5) -> list[list[float]]:
    """Same detector as `orange_redaction_boxes`, for an in-memory RGB image."""
    from scipy import ndimage

    hsv = np.asarray(im.convert("HSV")).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # PIL hue is 0..255; the overlay orange sits around 20..30 with high saturation
    mask = (h >= 15) & (h <= 32) & (s >= 150) & (v >= 180)
    mask = ndimage.binary_closing(mask, iterations=3)
    lab, n = ndimage.label(mask)
    boxes = []
    for sl in ndimage.find_objects(lab):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        area = hh * ww
        if not (min_area_frac * mask.size <= area <= max_area_frac * mask.size) or not (
                min_aspect * hh <= ww <= max_aspect * hh):
            continue
        fill = mask[sl].mean()
        if fill > 0.6:
            boxes.append([float(sl[1].start), float(sl[0].start), float(sl[1].stop), float(sl[0].stop)])
    return boxes
