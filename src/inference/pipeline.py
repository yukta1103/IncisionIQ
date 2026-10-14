"""Inference pipeline for incoming photos.

Every photo goes through the same overlay removal the mitigated model was
trained with (OCR text boxes plus orange redaction boxes, then inpainting), and
the pipeline logs, for every photo, whether any region was inpainted. The
step is not optional: `WoundPredictor.predict` always calls it.

    predictor = WoundPredictor.from_config("configs/phase3_convnext_tiny_inpainted.yaml")
    result = predictor.predict(Image.open("photo.jpg"))
    result["preprocess"]["inpainted"]   # True if any overlay region was removed
"""
import hashlib
import io
import logging
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps

from src.data.dataset import build_transforms, letterbox
from src.data.inpaint import inpaint_image, keep_text_box
from src.data.labels import HEAD_NAMES, HEADS
from src.data.ocr import ocr_image, orange_boxes_in_image
from src.eval.metrics import softmax
from src.models.multitask import MultiTaskNet
from src.utils import ROOT, load_config

log = logging.getLogger("incisioniq.inference")

OCR_LANG_PASSES = (("ch_sim", "en"), ("ru", "en"))  # same passes as the Phase 1 audit


class OverlayRemover:
    """OCR + orange-box detection + inpainting, identical to the training-time rule."""

    def __init__(self, gpu: bool | None = None):
        import easyocr

        gpu = torch.cuda.is_available() if gpu is None else gpu
        self.readers = [easyocr.Reader(list(langs), gpu=gpu, verbose=False) for langs in OCR_LANG_PASSES]

    def __call__(self, im: Image.Image) -> tuple[Image.Image, dict]:
        t0 = time.perf_counter()
        im = ImageOps.exif_transpose(im).convert("RGB")
        regions = []
        for reader in self.readers:
            for d in ocr_image(reader, im):
                if keep_text_box(d, 0.5, 2, 0.25, 3):
                    regions.append({"bbox": d["bbox"], "source": "ocr", "conf": round(d["conf"], 3)})
        for b in orange_boxes_in_image(im):
            regions.append({"bbox": b, "source": "orange_box"})
        clean = inpaint_image(im, [r["bbox"] for r in regions])
        report = {
            "inpainted": bool(regions),
            "n_regions": len(regions),
            "regions": regions,  # boxes only; OCR text is not stored, it may contain personal data
            "inpainted_area_frac": _area_frac(regions, im.width, im.height),
            "seconds": round(time.perf_counter() - t0, 3),
        }
        return clean, report


def _area_frac(regions, w, h) -> float:
    m = np.zeros((h, w), dtype=bool)
    for r in regions:
        x0, y0, x1, y1 = (int(round(v)) for v in r["bbox"])
        m[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = True
    return round(float(m.mean()), 4)


class WoundPredictor:
    """Ensemble of the five grouped-CV fold models of one experiment. Returns raw
    (uncalibrated) per-head probabilities; calibration and decision rules are
    applied on top (Phase 4 and 6)."""

    def __init__(self, cfg: dict, device: str | None = None, remover: OverlayRemover | None = None):
        if cfg.get("image_variant", "original") != "inpainted":
            raise ValueError("the deployed pipeline expects a model trained on inpainted images")
        self.cfg = cfg
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.remover = remover or OverlayRemover()
        self.tf = build_transforms(cfg, train=False)
        self.models = []
        for k in range(cfg["cv"]["n_splits"]):
            ck = torch.load(ROOT / cfg["checkpoint_dir"] / cfg["name"] / f"cv{k}.pt", weights_only=False,
                            map_location=self.device)
            m = MultiTaskNet(cfg["backbone"], {h: len(HEADS[h]["classes"]) for h in HEAD_NAMES}, pretrained=False)
            m.load_state_dict(ck["state_dict"])
            self.models.append(m.to(self.device).eval())

    @classmethod
    def from_config(cls, path: str | Path, **kw):
        return cls(load_config(ROOT / path), **kw)

    def _input(self, clean: Image.Image) -> torch.Tensor:
        u8 = torch.from_numpy(np.array(letterbox(clean, self.cfg["cache_size"]))).permute(2, 0, 1)
        return self.tf(u8).unsqueeze(0).to(self.device)

    def _models(self, fold: int | None):
        return self.models if fold is None else [self.models[fold]]

    @torch.no_grad()
    def predict(self, im: Image.Image, photo_id: str | None = None, fold: int | None = None) -> dict:
        """fold=None: 5-model ensemble (uploaded photos). fold=k: only fold k's model, for
        images that model never trained on (out-of-fold demo examples)."""
        photo_id = photo_id or _photo_hash(im)
        clean, report = self.remover(im)
        log.info("photo=%s inpainted=%s regions=%d area=%.4f ocr_s=%.2f", photo_id, report["inpainted"],
                 report["n_regions"], report["inpainted_area_frac"], report["seconds"])
        x = self._input(clean)
        with torch.autocast("cuda", dtype=torch.float16, enabled=self.device == "cuda"):  # as in evaluation
            outs = [m(x) for m in self._models(fold)]
        per_model = [{h: softmax(o[h].float().cpu().numpy())[0] for h in HEAD_NAMES} for o in outs]
        probs = {h: np.mean([pm[h] for pm in per_model], axis=0) for h in HEAD_NAMES}
        return {
            "photo_id": photo_id,
            "preprocess": report,
            "probs": {h: dict(zip(HEADS[h]["classes"], map(float, probs[h]))) for h in HEAD_NAMES},
            "probs_array": {h: probs[h].tolist() for h in HEAD_NAMES},
            "fold_spread": {h: float(np.std([pm[h] for pm in per_model], axis=0).max()) for h in HEAD_NAMES},
            "model": self.cfg["name"] + (f" (fold {fold})" if fold is not None else " (5-model ensemble)"),
            "clean_image": clean,
            "size": im.size,
        }

    def gradcam(self, clean: Image.Image, head: str, target_class: int, fold: int | None = None):
        """Grad-CAM (fp32) for one head's class, averaged over the models used, plus the
        letterboxed display image it aligns with."""
        from src.explain.gradcam import gradcam_maps

        x = self._input(clean)
        cams = [gradcam_maps(m, x, head, target_class, batch_size=1)[0] for m in self._models(fold)]
        cam = np.mean(cams, axis=0)
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        disp = np.array(letterbox(clean, self.cfg["input_size"]))
        return cam, disp


def _photo_hash(im: Image.Image) -> str:
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    return hashlib.sha256(buf.getvalue()).hexdigest()[:12]
