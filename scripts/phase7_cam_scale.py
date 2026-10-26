"""Phase 7: one fixed display scale for the demo's Grad-CAM.

The demo used to stretch every heat map to full brightness, so a weak map looked as strong as a
strong one. It now divides the raw Grad-CAM by one constant: the 95th percentile of the
per-image maximum raw value over fold 0's held-out images (images the deployed fold 0 model never
trained on), preprocessed as in training (stored OCR and redaction boxes, inpainted). Maps
brighter than that saturate.

Also checks that the raw map, min-max normalized, matches pytorch-grad-cam's map (the Phase 3
audit tool), so the two use the same Grad-CAM.

Usage: python scripts/phase7_cam_scale.py      writes results/phase7/cam_scale.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.inpaint import inpaint_image, overlay_boxes  # noqa: E402
from src.explain.gradcam import gradcam_maps, gradcam_raw  # noqa: E402
from src.inference.pipeline import WoundPredictor  # noqa: E402
from src.utils import ROOT, load_config, save_json  # noqa: E402

PERCENTILE = 95
INFECTION_ELEVATED = 1


def main():
    dep = json.loads((ROOT / "results" / "phase6" / "deployment.json").read_text(encoding="utf-8"))
    fold = dep["deployed_fold"]
    cfg = load_config(ROOT / dep["config"])
    proc = ROOT / cfg["processed_dir"]
    sp = pd.read_csv(ROOT / cfg["results_dir"] / "splits.csv")
    names = sorted(sp[sp.cv_fold == fold].image_name, key=lambda n: int(n.removesuffix(".jpg")))
    boxes = overlay_boxes(proc / "ocr.json", proc / "orange_boxes.json")
    pred = WoundPredictor(cfg, remover=object(), folds=[fold])
    model = pred.models[fold]

    maxima, corr = [], []
    for i, n in enumerate(names):
        x = pred._input(inpaint_image(Image.open(proc / "images" / n), boxes.get(n, [])))
        raw = gradcam_raw(model, x, "infection", INFECTION_ELEVATED)
        maxima.append(float(raw.max()))
        if i < 20:  # equivalence check against the library on the first 20 images
            lib = gradcam_maps(model, x, "infection", INFECTION_ELEVATED, batch_size=1)[0]
            if raw.max() > 0 and lib.std() > 0:
                corr.append(float(np.corrcoef((raw / raw.max()).ravel(), lib.ravel())[0, 1]))
    maxima = np.array(maxima)
    scale = float(np.percentile(maxima, PERCENTILE))
    out = {"scale": scale, "percentile": PERCENTILE, "cv_fold": fold, "n_images": len(names),
           "head": "infection", "target_class": "elevated",
           "per_image_max": {"min": float(maxima.min()), "median": float(np.median(maxima)),
                             "p95": scale, "max": float(maxima.max())},
           "median_max_relative_to_scale": float(np.median(maxima) / scale),
           "check_corr_with_pytorch_grad_cam": {"n": len(corr), "min": float(min(corr)), "median": float(np.median(corr))}}
    save_json(out, ROOT / "results" / "phase7" / "cam_scale.json")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    torch.manual_seed(0)
    main()
